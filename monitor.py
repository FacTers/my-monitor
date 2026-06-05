import os
import time
import requests
from bs4 import BeautifulSoup
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
URL = "https://nude-moon.org"
DB_FILE = "last_order.txt"

# Пустой веб-сервер, чтобы Render думал, что это сайт и держал его бесплатно
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running...")

def run_web_server():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), SimpleHTTPRequestHandler)
    server.serve_forever()

def send_telegram(message):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except Exception as e: print(f"TG Error: {e}")

def monitor_logic():
    print("Мониторинг запущен в фоновом режиме...")
    while True:
        try:
            response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                last_order_element = soup.find("a", href=lambda href: href and href.startswith("/order/"))
                if last_order_element:
                    order_url = "https://nude-moon.org" + last_order_element.get("href")
                    order_title = last_order_element.text.strip()
                    
                    try:
                        with open(DB_FILE, "r", encoding="utf-8") as f: last_saved_url = f.read().strip()
                    except FileNotFoundError: last_saved_url = ""

                    if order_url != last_saved_url:
                        with open(DB_FILE, "w", encoding="utf-8") as f: f.write(order_url)
                        send_telegram(f"🔔 *Новый заказ на сайте!*\n\n📌 Название: {order_title}\n🔗 Ссылка: {order_url}")
        except Exception as e:
            print(f"Loop Error: {e}")
        time.sleep(3600) # Проверка раз в час

if __name__ == "__main__":
    # Запускаем логику парсера в отдельном потоке, а веб-сервер в основном
    Thread(target=monitor_logic, daemon=True).start()
    run_web_server()
