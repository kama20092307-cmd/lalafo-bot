import os
import time
import threading
import requests
import telebot
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

TOKEN = '8740369059:AAHOgepptLqDaTuomKNp6PsmlQyvjPXoccA'
USERS = [8475243990, 6642526111]

bot = telebot.TeleBot(TOKEN)
seen_ids = set()

# Мобильный эндпоинт v2 с авторизацией гостя
SEARCH_URL = "https://lalafo.kg/api/2.0/feed"

def send_async_message(user_id, text):
    try:
        bot.send_message(user_id, text, parse_mode='Markdown')
        print(f"✅ Сообщение отправлено {user_id}")
    except Exception as e:
        print(f"⚠️ Ошибка отправки пользователю {user_id}: {e}")

def send_to_all(message_text):
    for uid in USERS:
        threading.Thread(target=send_async_message, args=(uid, message_text)).start()

def main_scraper_loop():
    print("Запуск обхода 403 Cloudflare...")
    time.sleep(3)
    send_to_all("🛡️ **Обход защиты применён! Ищу iPhone...**")
    
    # Имитируем запрос от официального мобильного приложения Android
    headers = {
        "User-Agent": "Lalafo/4.65.0 (Android; 13)",
        "Accept": "application/json",
        "Country-Id": "12",
        "Language": "ru_RU",
        "X-App-Version": "4.65.0"
    }

    session = requests.Session()

    while True:
        try:
            # Ищем конкретно по поисковому запросу "iphone" в категории телефонов
            params = {
                "q": "iphone",
                "limit": 20,
                "category_id": 1409,
                "sort_by": "created_at:desc"
            }
            
            response = session.get(SEARCH_URL, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', []) or data.get('feed', [])
                
                for item in items:
                    item_id = item.get('id')
                    if not item_id or item_id in seen_ids:
                        continue
                    
                    seen_ids.add(item_id)
                    
                    price = item.get('price')
                    title = item.get('title', 'iPhone')
                    
                    # Проверяем цену от 1 000 до 15 000 сом
                    if price and 1000 <= int(price) <= 15000:
                        price_val = int(price)
                        item_url = item.get('url', f"https://lalafo.kg/{item_id}")
                        if not item_url.startswith('http'):
                            item_url = "https://lalafo.kg" + item_url
                            
                        msg = (
                            f"🔥 **НАХОДКА ДО 15 000 СОМ!**\n\n"
                            f"📱 **{title}**\n"
                            f"💰 **Цена:** {price_val:,} KGS\n"
                            f"🔗 {item_url}"
                        ).replace(',', ' ')
                        
                        send_to_all(msg)
                        time.sleep(1)
            else:
                print(f"Статус ответа: {response.status_code}")

        except Exception as e:
            print(f"⚠️ Ошибка: {e}")

        time.sleep(25)

threading.Thread(target=main_scraper_loop, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    
