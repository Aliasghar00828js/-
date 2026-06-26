import os
import telebot
import google.generativeai as genai

# دریافت متغیرهای محیطی از تنظیمات Railway
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# پیکربندی هوش مصنوعی گوگل
genai.configure(api_key=GOOGLE_API_KEY)
# استفاده از مدل قدرتمند و سریع پیش‌فرض تو
model = genai.GenerativeModel('gemini-3-flash-preview')

# راه‌اندازی ربات تلگرام با توکن شما
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "سلام! من ربات هوش مصنوعی شما هستم. هر سوالی داری ازم بپرس تا جواب بدم.🤖")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        # فرستادن متن پیام کاربر به مدل هوش مصنوعی
        response = model.generate_content(message.text)
        # فرستادن پاسخ هوش مصنوعی به کاربر در تلگرام
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "آخ! یه مشکلی پیش آمد. دوباره تلاش کن یا بعداً امتحان کن. ❌")
        print(f"Error: {e}")

# روشن نگه داشتن ربات در حالت Polling
print("Bot is running...")
bot.infinity_polling()
