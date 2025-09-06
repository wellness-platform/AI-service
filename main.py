from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import requests
import os
import json
from models import SubtaskRequest, SubtaskResponse, SubtaskItem, SubtaskCategory
from mock_data import get_mock_subtasks

app = FastAPI(title="Task Decomposer API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DeepSeek API configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your-deepseek-api-key-here")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def call_deepseek_api(input_text: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Calls DeepSeek API to break down tasks into subtasks with priority and time estimates
    """
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    Analyze this task and break it down into subtasks with priority and time estimates:
    {input_text}
    
    Return ONLY JSON in this exact format:
    {{
      "category_name": [
        {{
          "name": "subtask name",
          "description": "detailed description",
          "priority": "high/medium/low",
          "estimated_time": "time estimate (e.g., 2 hours, 3 days, 1 week)"
        }}
      ]
    }}
    
    Rules:
    1. Priority: "high" for critical path tasks, "medium" for important but not urgent, "low" for nice-to-have
    2. Time estimates: be realistic based on typical development timelines
    3. Include 3-8 subtasks total
    4. Return ONLY JSON, no other text
    """
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a project manager expert. Analyze tasks and provide structured breakdowns with realistic time estimates and priorities. Always return valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,  # 👈 Lower temperature for more consistent results
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        ai_response = result['choices'][0]['message']['content']
        
        # Extract JSON from response
        json_start = ai_response.find('{')
        json_end = ai_response.rfind('}') + 1
        json_str = ai_response[json_start:json_end]
        
        return json.loads(json_str)
            
    except Exception as e:
        print(f"DeepSeek API call error: {e}")
        return get_mock_subtasks_with_metadata(input_text)  # 👈 Updated mock function

def format_subtasks(raw_tasks: Dict[str, List[Dict[str, str]]]) -> Dict[str, SubtaskCategory]:
    """
    Formats raw tasks into structured format
    """
    formatted = {}
    
    for category_name, tasks in raw_tasks.items():
        subtask_items = []
        
        for i, task_data in enumerate(tasks):
            # 👇 ВИМАГАЄМО всі поля від AI (без значень за замовчуванням)
            name = task_data['name']  # ← Обов'язкове поле
            description = task_data.get('description', '')  # ← Опціональне
            priority = task_data['priority']  # ← Обов'язкове (AI має повернути)
            estimated_time = task_data['estimated_time']  # ← Обов'язкове (AI має повернути)
            
            subtask_item = SubtaskItem(
                name=name,
                description=description,
                priority=priority,
                estimated_time=estimated_time
            )
            subtask_items.append(subtask_item)
        
        formatted[category_name] = SubtaskCategory(
            category_name=category_name,
            tasks=subtask_items
        )
    
    return formatted

@app.post("/decompose-tasks", response_model=SubtaskResponse)
async def decompose_tasks(request: SubtaskRequest):
    """
    Breaks down input text into structured subtasks
    """
    try:
        if request.use_mock or not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "your-deepseek-api-key-here":
            # Use mock data for testing
            raw_tasks = get_mock_subtasks_with_metadata(request.input_text)
            message = "Using mock data (by request or no API key)"
        else:
            # Call real API with fallback to mock data
            try:
                raw_tasks = call_deepseek_api(request.input_text)
                message = "Tasks decomposed using DeepSeek API"
            except Exception as api_error:
                print(f"API call failed, falling back to mock data: {api_error}")
                raw_tasks = get_mock_subtasks(request.input_text)
                message = "API call failed, using mock data as fallback"
        
        # Format results
        formatted_tasks = format_subtasks(raw_tasks)
        
        # Count total tasks
        total_tasks = sum(len(category.tasks) for category in formatted_tasks.values())
        
        return SubtaskResponse(
            success=True,
            subtasks=formatted_tasks,
            total_tasks=total_tasks,
            message=message
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Task Decomposer API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "task-decomposer"}

@app.get("/api-status")
async def api_status():
    """
    Check current API configuration status
    """
    status = {
        "api_configured": DEEPSEEK_API_KEY != "your-deepseek-api-key-here" and bool(DEEPSEEK_API_KEY),
        "current_mode": "MOCK" if DEEPSEEK_API_KEY == "your-deepseek-api-key-here" else "REAL_API",
        "message": "Using mock data" if DEEPSEEK_API_KEY == "your-deepseek-api-key-here" else "Ready for real API calls"
    }
    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)