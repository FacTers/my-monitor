import os
import requests
from bs4 import BeautifulSoup

# Получаем токены из настроек сервера
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
URL = "https://nude-moon.org"
DB_FILE = "last_order.txt"

def send_telegram(message):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Ошибка отправки в TG: {e}")

def main():
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Ошибка: Переменные окружения TELEGRAM_TOKEN или CHAT_ID не настроены!")
        return

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(URL, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Сайт вернул код: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.text, "html.parser")
        # Поиск первой ссылки на заказ
        last_order_element = soup.find("a", href=lambda href: href and href.startswith("/order/"))

        if last_order_element:
            order_url = "https://nude-moon.org" + last_order_element.get("href")
            order_title = last_order_element.text.strip()
            
            # Читаем старый ID
            try:
                with open(DB_FILE, "r", encoding="utf-8") as f:
                    last_saved_url = f.read().strip()
            except FileNotFoundError:
                last_saved_url = ""

            if order_url != last_saved_url:
                print(f"Новый заказ: {order_title}")
                with open(DB_FILE, "w", encoding="utf-8") as f:
                    f.write(order_url)
                
                msg = f"🔔 *Новый заказ на сайте!*\n\n📌 Название: {order_title}\n🔗 Ссылка: {order_url}"
                send_telegram(msg)
            else:
                print("Новых заказов нет.")
        else:
            print("Не удалось распарсить страницу.")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
