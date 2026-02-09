import feedparser
import requests
import os
import time
import json

# جلب البيانات من Secrets
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        response = requests.post(url, data=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ خطأ في الإرسال: {e}")
        return False

def check_feeds():
    try:
        with open('accounts.json', 'r', encoding='utf-8') as f:
            accounts = json.load(f)
    except Exception as e:
        print(f"❌ خطأ في قراءة ملف JSON: {e}")
        return False

    has_updates = False
    for account in accounts:
        try:
            # إضافة طابع زمني للرابط لمنع "الكاش" (Cache) من الموقع المزود
            feed_url = f"{account['rss_url']}&t={int(time.time())}"
            feed = feedparser.parse(feed_url)
            
            if not feed.entries:
                continue

            latest_entry = feed.entries[0]
            # تنظيف المعرف لضمان دقة المقارنة
            latest_id = str(latest_entry.id).strip()
            
            file_name = f"last_id_{account['name'].replace(' ', '_')}.txt"

            last_id = None
            if os.path.exists(file_name):
                with open(file_name, "r") as f:
                    last_id = f.read().strip()

            if latest_id != last_id:
                msg = (
                    f"<b>{account['prefix']}</b>\n"
                    f"👤 <b>الحساب:</b> {account['name']}\n"
                    f"📝 <b>المحتوى:</b> {latest_entry.title}\n\n"
                    f"🔗 <b>الرابط:</b> {latest_entry.link}"
                )
                
                if send_telegram_msg(msg):
                    print(f"✅ تم إرسال تحديث لـ {account['name']}")
                    with open(file_name, "w") as f:
                        f.write(latest_id)
                    has_updates = True
            else:
                print(f"⏳ لا جديد لـ {account['name']}")
                
        except Exception as e:
            print(f"⚠️ خطأ في فحص {account['name']}: {e}")
    
    return has_updates

if __name__ == "__main__":
    print("🚀 بدء تشغيل المراقبة الذكية...")
    start_time = time.time()
    
    # يعمل لمدة 10 دقائق (600 ثانية) في كل دورة
    while time.time() - start_time < 600:
        if check_feeds():
            # إذا وجد تحديث ننهي الدورة فوراً لحفظ المعرف الجديد في GitHub
            print("📦 تحديث المعرفات في الداتابيز...")
            break
        
        # الفحص كل 5 ثوانٍ لسرعة قصوى
        time.sleep(5)
