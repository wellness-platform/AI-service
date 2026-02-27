# Створення проекту та віртуального середовища
mkdir voice2tasks && cd voice2tasks
python3 -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate

# Встановлення залежностей для DeepSeek
pip install fastapi uvicorn python-multipart requests pydantic

uvicorn main:app --reload

export=<copypass> 

# POST запит до /decompose-tasks
curl -X POST "http://localhost:8000/decompose-tasks" \
     -H "Content-Type: application/json" \
     -d '{
       "input_text": "Мені потрібно розробити веб-додаток для керування проектами",
       "use_mock": true
     }'


# POST request to /decompose-tasks
curl -X POST "http://localhost:8000/decompose-tasks" \
     -H "Content-Type: application/json" \
     -d '{
       "input_text": "So i want to start creating a productivity app for people with adhd as a designer and don't know where to start"
     }'

curl -X POST "http://localhost:8000/decompose-tasks" \
     -H "Content-Type: application/json" \
     -d '{
       "input_text": "Develop a mobile app for fitness tracking",
       "use_mock": false  # 👈 Це головне!
     }'
# Test 
curl -X POST "http://localhost:8000/decompose-tasks"   -H "Content-Type: application/json"   -d '{"input_text": "any text", "use_test_file": "test3.json"}'

# Перелік тестових файлів:
curl http://localhost:8000/test-files


Best Practices які ми використали:
Environment-based configuration (API ключ через змінні оточення)

Clean separation тестового і продакшн режимів

Proper error handling з чіткими повідомленнями

API documentation автоматична через FastAPI

File organization логічна структура проект


curl -X POST "http://localhost:8000/decompose-tasks" \
  -H "Content-Type: application/json" \
  -d "{\"input_text\": \"So i want to start creating a productivity app for people with adhd as a designer and don't know where to start\"}"