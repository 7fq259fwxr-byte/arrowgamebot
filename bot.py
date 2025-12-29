import os
import json
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Разрешаем запросы с GitHub, чтобы не было ошибок CORS
CORS(app)

# Твой токен бота
BOT_TOKEN = "8124600551:AAHYE9GXQHmc3bAe1kABfqHBmmOKqQQliWU"
DATA_FILE = "/home/malollas/mysite/arrows_data.json"

# Вспомогательные функции для базы данных
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 1. ОБРАБОТКА БОТА (Сообщения /start)
@app.route('/api/telegram', methods=['POST'])
def telegram_webhook():
    update = request.get_json()
    if update and "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        if text == "/start":
            send_start_button(chat_id)
    return jsonify({"status": "ok"}), 200

def send_start_button(chat_id):
    # ОБЯЗАТЕЛЬНО: впиши сюда название своего репозитория вместо ВАШ_РЕПОЗИТОРИЙ
    game_url = "https://malollas.github.io/ВАШ_РЕПОЗИТОРИЙ/"
    method = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "🎮 Привет! Нажми на кнопку ниже, чтобы начать игру и ставить рекорды:",
        "reply_markup": {
            "inline_keyboard": [[
                {
                    "text": "Играть сейчас", 
                    "web_app": {"url": game_url}
                }
            ]]
        }
    }
    requests.post(method, json=payload)

# 2. АВТОРИЗАЦИЯ ИГРОКА (Чтобы появились стрелки)
@app.route('/api/get_user', methods=['POST'])
def get_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data received"}), 400
            
        user_id = str(data.get('user_id', 'unknown'))
        username = data.get('username', 'Guest')

        users = load_data()

        if user_id not in users:
            users[user_id] = {
                "username": username,
                "score": 0,
                "games_played": 0,
                "last_active": time.strftime('%Y-%m-%d %H:%M:%S')
            }
            save_data(users)

        return jsonify({
            "success": True,
            "user": users[user_id]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 3. ТЕСТОВЫЕ И ДОПОЛНИТЕЛЬНЫЕ ЭНДПОИНТЫ
@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({
        "success": True, 
        "message": "API работает нормально!",
        "server_time": time.strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    users = load_data()
    # Сортируем топ-10 по очкам
    sorted_users = sorted(users.values(), key=lambda x: x.get('score', 0), reverse=True)[:10]
    return jsonify(sorted_users)

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    webhook_url = "https://malollas.pythonanywhere.com/api/telegram"
    method = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={webhook_url}"
    r = requests.get(method)
    return r.text
