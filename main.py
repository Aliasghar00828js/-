import os
import logging
import telebot
from groq import Groq
from flask import Flask, request

# تنظیم سیستم لاگینگ برای مانیتورینگ دقیق در پنل Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# دریافت متغیرهای محیطی
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
RAILWAY_DOMAIN = os.environ.get('RAILWAY_PUBLIC_DOMAIN')

# اعتبارسنجی اولیه متغیرها برای جلوگیری از کرش سرور
if not BOT_TOKEN or not GROQ_API_KEY:
    logging.critical("Error: BOT_TOKEN or GROQ_API_KEY is missing in environment variables!")
    raise ValueError("Missing critical environment variables.")

# راه‌اندازی ربات تلگرام، کلاینت Groq و وب‌سرور Flask
bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)
app = Flask(__name__)

# دریافت داینامیک اطلاعات ربات جهت شناسایی در گروه‌ها
try:
    BOT_INFO = bot.get_me()
    BOT_ID = BOT_INFO.id
    BOT_USERNAME = BOT_INFO.username
    logging.info(f"Bot @{BOT_USERNAME} successfully initialized.")
except Exception as e:
    logging.critical(f"Failed to connect to Telegram API: {e}")
    raise e

# مسیر ایمن وب‌هوک (استفاده از توکن در URL جهت جلوگیری از دسترسی‌های غیرمجاز)
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        logging.warning("Received unauthorized request or invalid content-type.")
        return 'Forbidden', 403

# صفحه اصلی سرور برای پینگ کردن و تست سلامت (Health Check)
@app.route('/')
def index():
    return f"Bot @{BOT_USERNAME} is running in production mode (Webhook).", 200

# مدیریت دستورات start و help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "سلام! ربات متصل به Groq در حالت حرفه‌ای (Webhook) فعال و آماده پاسخگویی است.")

# مدیریت و پردازش تمام پیام‌های ورودی
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    try:
        # ۱. بررسی چت شخصی
        is_private = message.chat.type == 'private'
        
        # ۲. بررسی تگ شدن آیدی ربات در متن پیام
        is_mentioned = message.text and f"@{BOT_USERNAME}" in message.text
        
        # ۳. بررسی ریپلای شدن روی پیام‌های این ربات (چه توسط کاربر، چه بات‌های دیگر)
        is_reply_to_bot = False
        if message.reply_to_message and message.reply_to_message.from_user:
            if message.reply_to_message.from_user.id == BOT_ID:
                is_reply_to_bot = True

        # ربات فقط در این ۳ حالت زمان و هزینه API را صرف پاسخگویی می‌کند
        if is_private or is_mentioned or is_reply_to_bot:
            user_text = message.text if message.text else ""
            
            # پاکسازی تگ ربات از متن جهت بهینه‌سازی پرامپت ارسالی به هوش مصنوعی
            if is_mentioned:
                user_text = user_text.replace(f"@{BOT_USERNAME}", "").strip()

            # اگر پیام ارسالی متنی نداشت (مثلاً فقط تگ خالی یا رسانه بدون کپشن بود) رد کند
            if not user_text:
                return

            # درخواست پاسخ از مدل پرسرعت و بهینه Llama 3.1 در سرورهای Groq
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "user", "content": user_text}
                ]
            )
            
            ai_response = completion.choices[0].message.content
            
            if ai_response:
                bot.reply_to(message, ai_response)

    except Exception as e:
        logging.error(f"Error processing message from chat {message.chat.id}: {e}")

# اجرای نهایی پروژه و تنظیمات وب‌هوک هنگام بالا آمدن سرور
if __name__ == "__main__":
    try:
        # حذف هوشمندانه وب‌هوک‌های قبلی تلگرام برای جلوگیری از تداخل علمی
        bot.remove_webhook()
        
        if RAILWAY_DOMAIN:
            webhook_url = f"https://{RAILWAY_DOMAIN}/{BOT_TOKEN}"
            bot.set_webhook(url=webhook_url)
            logging.info(f"Webhook successfully configured and pointed to: {webhook_url}")
        else:
            logging.warning("RAILWAY_PUBLIC_DOMAIN not detected. Running without setting up dynamic webhook.")
            
    except Exception as e:
        logging.error(f"Error during webhook setup: {e}")

    # گوش دادن به پورت اختصاص داده شده توسط Railway (پیش‌فرض روی پورت 5000)
    port = int(os.environ.get("PORT", 5000))
    logging.info(f"Starting Flask server on port {port}...")
    app.run(host="0.0.0.0", port=port)
            
