import requests
import json
from config import TOKEN

def generate_response(user_input, tokens=200):
    url = "http://localhost:1234/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    data = {
        "messages": [
            {"role": "system", "content": "Чат сессия с ИИ."},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7,
        "max_tokens": tokens,
        "stream": False
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        response_data = response.json()
        return response_data['choices'][0]['message']['content']
    else:
        return "Произошла ошибка при обработке вашего запроса, пожалуйста, попробуйте еще раз."
