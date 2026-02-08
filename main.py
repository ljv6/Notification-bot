import feedparser
import requests
import os
import time
import json

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Error: {e}")

def check_feeds():
    # فتح ملف الروابط وقراءته
    with open('accounts.json', 'r', encoding='utf-8') as f:
        accounts = json.load(f)

    for account in accounts:
        try:
            feed = feedparser.parse(account['rss_url'])
            if not feed.entries: continue

            latest_entry = feed.entries[0]
            latest_id = latest_entry.id
            file_name = f"last_id_{account['name'].replace(' ', '_')}.txt"

            if os.path.exists(file_name):
                with open(file_name, "r") as f:
                    last_id = f.read().strip()
            else:
                last_id = None

            if latest_id != last_id:
                msg = f"<b>{account['prefix']}</b>\n{latest_entry.title}\n{latest_entry.link}"
                send_telegram_msg(msg)
                with open(file_name, "w") as f:
                    f.write(latest_id)
                return True
        except Exception as e:
            print(f"Error checking {account['name']}: {e}")
    return False

if __name__ == "__main__":
    start_time = time.time()
    # السكربت يفحص كل 10 ثواني لمدة 10 دقائق في كل دورة تشغيل
    while time.time() - start_time < 600:
        if check_feeds():
            break
        time.sleep(10)
