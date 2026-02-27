from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import requests
import os
from pathlib import Path
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

def load_test_response(file_name: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Load test response from JSON file
    """
    try:
        # Шукаємо файл в папці test_responses
        file_path = Path(f"test_responses/{file_name}")
        if not file_path.exists():
            # Якщо не знайдено, шукаємо в корені
            file_path = Path(file_name)
            if not file_path.exists():
                raise FileNotFoundError(f"Test file {file_name} not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"✅ Loaded test data from {file_path}")
            return data
            
    except Exception as e:
        print(f"❌ Error loading test file {file_name}: {e}")
        raise HTTPException(status_code=404, detail=f"Test file error: {str(e)}")

def call_deepseek_api(input_text: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Calls DeepSeek API to break down tasks into subtasks with priority and time estimates
    """
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "your-deepseek-api-key-here":
        raise HTTPException(status_code=400, detail="DeepSeek API key not configured")

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
        print("🚀 Calling DeepSeek API...")
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
        print(f"❌ DeepSeek API call failed: {e}")
        raise HTTPException(status_code=500, detail=f"API call failed: {str(e)}")

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
    Main endpoint - uses either test file or real API
    """
    try:
        # 👇 1. TEST MODE - з тестового файлу
        if request.use_test_file:
            raw_tasks = load_test_response(request.use_test_file)
            message = f"Test mode: using {request.use_test_file}"
        
        # 👇 2. PRODUCTION MODE - реальне API
        else:
            try:
                raw_tasks = call_deepseek_api(request.input_text)
                message = "Tasks decomposed using DeepSeek API"
            except Exception as api_error:
                print(f"API call failed: {api_error}")
                raise HTTPException(status_code=500, detail=f"API call failed: {str(api_error)}")
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/test-files")
async def list_test_files():
    """List available test files"""
    test_dir = Path("test_responses")
    files = []
    
    if test_dir.exists():
        files = [f.name for f in test_dir.glob("*.json")]
    
    return {"available_test_files": files}

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