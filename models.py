from pydantic import BaseModel
from typing import List, Dict, Optional

class SubtaskRequest(BaseModel):
    input_text: str
    use_test_file: Optional[str] = None  # Для тестування без реального API

class SubtaskItem(BaseModel):
    name: str
    description: Optional[str] = None
    priority: str = "medium"  # low, medium, high
    estimated_time: Optional[str] = None

class SubtaskCategory(BaseModel):
    category_name: str
    tasks: List[SubtaskItem]

class SubtaskResponse(BaseModel):
    success: bool
    subtasks: Dict[str, SubtaskCategory]
    total_tasks: int
    message: Optional[str] = None


# from typing import List, Dict, Any

# def get_mock_subtasks_with_metadata(input_text: str) -> Dict[str, List[Dict[str, str]]]:
#     """
#     Returns mock response with subtasks including priority and time estimates
#     """
#     input_text_lower = input_text.lower()
    
#     # Base mock data with metadata
#     mock_tasks_with_metadata = {
#         "project_planning": [
#             {
#                 "name": "Define Requirements",
#                 "description": "Gather and document project requirements and specifications",
#                 "priority": "high",
#                 "estimated_time": "2-3 days"
#             },
#             {
#                 "name": "Create Project Plan",
#                 "description": "Develop detailed project timeline and milestones",
#                 "priority": "high",
#                 "estimated_time": "1-2 days"
#             }
#         ],
#         "development": [
#             {
#                 "name": "Setup Development Environment",
#                 "description": "Configure IDE, version control, and development tools",
#                 "priority": "high",
#                 "estimated_time": "1 day"
#             },
#             {
#                 "name": "Implement Core Features",
#                 "description": "Develop main functionality based on requirements",
#                 "priority": "high",
#                 "estimated_time": "2-3 weeks"
#             }
#         ],
#         "design": [
#             {
#                 "name": "UI/UX Design",
#                 "description": "Create user interface designs and user experience flows",
#                 "priority": "medium",
#                 "estimated_time": "1 week"
#             }
#         ]
#     }
    
#     # Return appropriate category based on input
#     if any(word in input_text_lower for word in ['plan', 'planning', 'strategy']):
#         return {"project_planning": mock_tasks_with_metadata["project_planning"]}
#     elif any(word in input_text_lower for word in ['design', 'ui', 'ux']):
#         return {"design": mock_tasks_with_metadata["design"]}
#     else:
#         return mock_tasks_with_metadata


# # 👇 Додай стару функцію для сумісності (якщо потрібно)
# def get_mock_subtasks(input_text: str) -> Dict[str, List[str]]:
#     """
#     Legacy function for backward compatibility
#     """
#     complex_data = get_mock_subtasks_with_metadata(input_text)
#     simple_data = {}
    
#     for category, tasks in complex_data.items():
#         simple_data[category] = [task["description"] for task in tasks]
    
#     return simple_data