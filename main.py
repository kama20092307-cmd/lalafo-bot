import os
import re
import time
import threading
import cloudscraper
from bs4 import BeautifulSoup
import telebot
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

TOKEN = '8740369059:AAHOgepptLqDaTuomKNp6PsmlQyvjPXoccA'
USERS = [8475243990, 6642526111]

bot = telebot.TeleBot(TOKEN)
BASE_URL = "https://lalafo.kg/kyrgyzstan/mobilnye-telefony-i-aksessuary/mobilnye-telefony"
seen_links = set()

def send_async_message(user_id, text):
    try:
        bot.send_message(user_id, text, parse_mode='Markdown')
        print(f"✅ Сообщение отправлено {user_id}")
    except Exception as e:
        print(f"⚠️ Ошибка отправки пользователю {user_id}: {e}")

def send_to_all(message_text):
    for uid in USERS:
        threading.Thread(target=send_async_message, args=(uid, message_text)).start()

def extract_real_price(article_soup):
    text = article_soup.text
    matches = re.findall(r'(\d[\d\s\.]*)\s*(?:kgs|сом|сомов|c|сом\.)', text, re.IGNORECASE)
    
    for match in matches:
        clean_num = re.sub(r'[\s\.]', '', match)
        if clean_num.isdigit():
            val = int(clean_num)
            if 500 <= val <= 300000:
                return val
                
    price_tags = article_soup.find_all(['p', 'span', 'div'], class_=lambda c: c and 'price' in c.lower())
    for p_tag in price_tags:
        nums = re.findall(r'\d+', p_tag.text.replace(' ', ''))
        if nums:
            val = int(nums[0])
            if 500 <= val <= 300000:
                return val

    return None

def process_page_articles(articles):
    found_count = 0
    for art in articles:
        link_tag = art.find('a', href=True)
        if not link_tag:
            continue
            
        full_link = "https://lalafo.kg" + link_tag['href'] if link_tag['href'].startswith('/') else link_tag['href']
        
        # Если ссылку уже отправляли — пропускаем (защита от повторов)
        if full_link in seen_links:
            continue
        
        seen_links.add(full_link)
        full_text = art.text.lower()
        
        if 'iphone' in full_text or 'айфон' in full_text:
            price = extract_real_price(art)
            
            if price and 1000 <= price <= 15000:
                msg = (
                    f"🔥 **НАХОДКА ДО 15 000 СОМ!**\n\n"
                    f"💰 **Цена:** {price} KGS\n"
                    f"🔗 {full_link}"
                )
                send_to_all(msg)
                found_count += 1
                time.sleep(1) # Небольшая пауза между сообщениями в Telegram
    return found_count

def main_scraper_loop():
    print("Запуск мониторинга на облачном хостинге...")
    time.sleep(3)
    send_to_all("🔎 **Сканирую существующих и новых iPhone до 15 000 сом...**")
    
    check_count = 0
    while True:
        try:
            check_count += 1
            scraper = cloudscraper.create_scraper()
            
            # Проверяем первые 2 страницы текущей ленты
            for page in range(1, 3):
                fresh_url = f"{BASE_URL}?page={page}&sort_by=created_at%3Adesc&_cache_bust={int(time.time())}"
                response = scraper.get(fresh_url, timeout=20)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    articles = soup.find_all('article')
                    process_page_articles(articles)
                else:
                    print(f"Статус ответа страницы {page}: {response.status_code}")
                time.sleep(2)

        except Exception as e:
            print(f"⚠️ Ошибка: {e}. Повтор через 15 сек...")
            time.sleep(15)
            continue

        time.sleep(20)

threading.Thread(target=main_scraper_loop, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    
