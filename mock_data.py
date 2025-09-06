from typing import List, Dict, Any

# Мок-дані для тестування без реального виклику API
mock_tasks_data = {
    "project_planning": [
        "Створити детальний план проекту",
        "Визначити основні етапи розробки",
        "Скласти список необхідних ресурсів"
    ],
    "development": [
        "Налаштувати середовище розробки",
        "Реалізувати основну функціональність",
        "Написати unit-тести"
    ],
    "testing": [
        "Провести інтеграційне тестування",
        "Виправити знайдені помилки",
        "Оптимізувати продуктивність"
    ],
    "deployment": [
        "Підготувати сервер для деплою",
        "Налаштувати CI/CD пайплайн",
        "Задеплоїти додаток"
    ]
}

def get_mock_subtasks(input_text: str) -> Dict[str, List[str]]:
    """
    Повертає мок-відповідь з підзавданнями на основі ключових слів у тексті
    """
    input_text_lower = input_text.lower()
    
    if any(word in input_text_lower for word in ['план', 'планування', 'plan']):
        return {"project_planning": mock_tasks_data["project_planning"]}
    
    elif any(word in input_text_lower for word in ['розробка', 'код', 'develop']):
        return {"development": mock_tasks_data["development"]}
    
    elif any(word in input_text_lower for word in ['тест', 'testing', 'тестування']):
        return {"testing": mock_tasks_data["testing"]}
    
    elif any(word in input_text_lower for word in ['деплой', 'deploy', 'запуск']):
        return {"deployment": mock_tasks_data["deployment"]}
    
    # Якщо не знайдено конкретної категорії, повертаємо всі задачі
    return mock_tasks_data