import os
import time
import threading
import cloudscraper
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

API_URL = "https://lalafo.kg/api/1.0/open/feed"

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
    print("Запуск проверки связи с API...")
    time.sleep(3)
    send_to_all("🧪 **Запуск проверки! Сейчас пришлю первые 5 любых телефонов с сайта...**")
    
    scraper = cloudscraper.create_scraper()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Country-Id": "12"
    }

    while True:
        try:
            params = {
                "expand": "url",
                "page": "1",
                "per-page": "20",
                "category_id": "1409"
            }
            
            response = scraper.get(API_URL, headers=headers, params=params, timeout=15)
            print(f"Статус ответа: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                count = 0
                for item in items:
                    item_id = item.get('id')
                    if not item_id or item_id in seen_ids:
                        continue
                    
                    seen_ids.add(item_id)
                    title = item.get('title', 'Без названия')
                    price = item.get('price', '0')
                    item_url = item.get('url', f"https://lalafo.kg/{item_id}")
                    if not item_url.startswith('http'):
                        item_url = "https://lalafo.kg" + item_url
                    
                    msg = f"📱 **Тест:** {title}\n💰 **Цена:** {price} KGS\n🔗 {item_url}"
                    send_to_all(msg)
                    
                    count += 1
                    if count >= 5: # Берём только 5 штук для теста
                        break
                    time.sleep(1)
            else:
                send_to_all(f"⚠️ Ошибка ответа API Lalafo: Код {response.status_code}")

        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
            send_to_all(f"⚠️ Сбой выполнения: {e}")

        time.sleep(30)

threading.Thread(target=main_scraper_loop, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    
