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

# Прямой URL API Lalafo для категории "Мобильные телефоны"
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
    print("Запуск мониторинга через API Lalafo...")
    time.sleep(3)
    send_to_all("🚀 **Бот переведён на прямой поиск API Lalafo!**\nСканирую текущие объявления...")
    
    check_count = 0
    scraper = cloudscraper.create_scraper()

    # Специальные заголовки, чтобы Lalafo отдавал полный список JSON
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Country-Id": "12" # Кыргызстан
    }

    while True:
        try:
            check_count += 1
            # Запрашиваем 40 самых свежих объявлений из категории телефонов
            params = {
                "expand": "url",
                "page": "1",
                "per-page": "40",
                "category_id": "1409", # Категория "Мобильные телефоны"
                "sort_by": "created_at:desc"
            }
            
            response = scraper.get(API_URL, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                for item in items:
                    item_id = item.get('id')
                    if not item_id or item_id in seen_ids:
                        continue
                    
                    seen_ids.add(item_id)
                    
                    title = item.get('title', '').lower()
                    description = item.get('description', '').lower()
                    full_text = f"{title} {description}"
                    
                    # Проверяем, что это iPhone / Айфон
                    if 'iphone' in full_text or 'айфон' in full_text:
                        price = item.get('price')
                        
                        # Фильтр цены: от 1 000 до 15 000 сом
                        if price and 1000 <= int(price) <= 15000:
                            price_val = int(price)
                            item_url = item.get('url', f"https://lalafo.kg/kyrgyzstan/mobilnye-telefony-i-aksessuary/mobilnye-telefony/{item_id}")
                            if not item_url.startswith('http'):
                                item_url = "https://lalafo.kg" + item_url
                                
                            item_title = item.get('title', 'iPhone')
                            
                            msg = (
                                f"🔥 **НАХОДКА ДО 15 000 СОМ!**\n\n"
                                f"📱 **{item_title}**\n"
                                f"💰 **Цена:** {price_val:,} KGS\n"
                                f"🔗 {item_url}"
                            ).replace(',', ' ')
                            
                            send_to_all(msg)
                            print(f"⚡ Находка через API: {item_title} за {price_val} сом")
                            time.sleep(1)
            else:
                print(f"Статус ответа API: {response.status_code}")

        except Exception as e:
            print(f"⚠️ Ошибка API: {e}. Повтор через 15 сек...")
            time.sleep(15)
            continue

        time.sleep(20)

threading.Thread(target=main_scraper_loop, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    
