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

SEARCH_URL = "https://lalafo.kg/api/2.0/feed"

PRICE_MIN = 1000
PRICE_MAX = 15000

def send_async_message(user_id, text):
    try:
        bot.send_message(user_id, text, parse_mode='Markdown')
        print(f"✅ Сообщение отправлено {user_id}", flush=True)
    except Exception as e:
        print(f"⚠️ Ошибка отправки пользователю {user_id}: {e}", flush=True)

def send_to_all(message_text):
    for uid in USERS:
        threading.Thread(target=send_async_message, args=(uid, message_text)).start()

def main_scraper_loop():
    print("Запуск расширенного поиска iPhone...", flush=True)
    time.sleep(3)
    send_to_all("🎯 **Бот переведён на расширенный глобальный поиск!**\nСканирую все объявления без ограничений по категориям...")

    headers = {
        "User-Agent": "Lalafo/4.65.0 (Android; 13)",
        "Accept": "application/json",
        "Country-Id": "12",
        "Language": "ru_RU",
        "X-App-Version": "4.65.0"
    }

    session = requests.Session()

    keywords = ["iphone", "айфон"]
    cycle_count = 0

    while True:
        cycle_count += 1
        print(f"\n===== Цикл #{cycle_count} =====", flush=True)
        try:
            for kw in keywords:
                params = {
                    "q": kw,
                    "limit": 30,
                    "sort_by": "created_at:desc"
                }

                response = session.get(SEARCH_URL, headers=headers, params=params, timeout=15)

                print(f"[{kw}] HTTP статус: {response.status_code}", flush=True)

                if cycle_count == 1:
                    send_to_all(f"🔧 Диагностика [{kw}]: HTTP статус {response.status_code}, длина ответа {len(response.text)}")

                if response.status_code == 200:
                    try:
                        data = response.json()
                    except Exception as e:
                        print(f"[{kw}] ⚠️ Не удалось распарсить JSON: {e}", flush=True)
                        print(f"[{kw}] Сырой ответ (первые 500 симв.): {response.text[:500]}", flush=True)
                        continue

                    print(f"[{kw}] Ключи верхнего уровня в ответе: {list(data.keys())}", flush=True)

                    items = data.get('items', []) or data.get('feed', [])
                    print(f"[{kw}] Найдено объявлений в ответе: {len(items)}", flush=True)

                    if len(items) == 0:
                        print(f"[{kw}] Пример сырого ответа: {response.text[:800]}", flush=True)
                        if cycle_count == 1:
                            send_to_all(f"🔧 [{kw}]: объявлений 0. Сырой ответ: {response.text[:300]}")

                    new_count = 0
                    for item in items:
                        item_id = item.get('id')
                        if not item_id or item_id in seen_ids:
                            continue

                        seen_ids.add(item_id)
                        new_count += 1

                        price = item.get('price')
                        title = item.get('title', 'iPhone')

                        print(f"[{kw}] Новое объявление: id={item_id}, price={price}, title={title}", flush=True)

                        if price and PRICE_MIN <= int(price) <= PRICE_MAX:
                            price_val = int(price)
                            item_url = item.get('url', f"https://lalafo.kg/{item_id}")
                            if not item_url.startswith('http'):
                                item_url = "https://lalafo.kg" + item_url

                            msg = (
                                f"🔥 **НАХОДКА ДО {PRICE_MAX:,} СОМ!**\n\n"
                                f"📱 **{title}**\n"
                                f"💰 **Цена:** {price_val:,} KGS\n"
                                f"🔗 {item_url}"
                            ).replace(',', ' ')

                            send_to_all(msg)
                            time.sleep(1)

                    print(f"[{kw}] Новых объявлений за этот проход: {new_count}", flush=True)

                else:
                    print(f"[{kw}] ⚠️ Плохой статус: {response.status_code}", flush=True)
                    print(f"[{kw}] Ответ сервера: {response.text[:500]}", flush=True)
                    if cycle_count == 1:
                        send_to_all(f"🔧 [{kw}]: плохой статус {response.status_code}. Ответ: {response.text[:300]}")

                time.sleep(3)

        except Exception as e:
            print(f"⚠️ Ошибка в цикле: {e}", flush=True)
            if cycle_count == 1:
                send_to_all(f"🔧 Ошибка в цикле: {e}")

        time.sleep(20)

threading.Thread(target=main_scraper_loop, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
