# Створення проекту та віртуального середовища
mkdir voice2tasks && cd voice2tasks
python3 -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate

# Встановлення залежностей для DeepSeek
pip install fastapi uvicorn python-multipart requests pydantic


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
       "input_text": "I need to develop a web application for project management",
       "use_mock": true
     }'

curl -X POST "http://localhost:8000/decompose-tasks" \
     -H "Content-Type: application/json" \
     -d '{
       "input_text": "Develop a mobile app for fitness tracking",
       "use_mock": false  # 👈 Це головне!
     }'