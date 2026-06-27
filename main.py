import os
import telebot
from groq import Groq

# دریافت توکن‌ها از متغیرهای محیطی Railway
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

# راه‌اندازی ربات تلگرام و ابزار Groq
bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

# دریافت اطلاعات ربات (شناسه و نام کاربری) برای مدیریت پیام‌های گروه
BOT_INFO = bot.get_me()
BOT_ID = BOT_INFO.id
BOT_USERNAME = BOT_INFO.username

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "ربات متصل به Groq آماده استفاده است!")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    try:
        # بررسی وضعیت پیام (چت شخصی، تگ شدن ربات، یا ریپلای به ربات)
        is_private = message.chat.type == 'private'
        is_mentioned = message.text and f"@{BOT_USERNAME}" in message.text
        is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.id == BOT_ID

        # ربات فقط در این ۳ حالت پردازش را انجام می‌دهد
        if is_private or is_mentioned or is_reply_to_bot:
            
            user_text = message.text if message.text else ""
            
            # پاک کردن تگ ربات از متن پیام تا در پاسخ هوش مصنوعی اختلال ایجاد نکند
            if is_mentioned:
                user_text = user_text.replace(f"@{BOT_USERNAME}", "").strip()

            # ارسال متن به مدل Llama 3 روی سرورهای پرسرعت Groq
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "user", "content": user_text}
                ]
            )
            
            # ارسال پاسخ نهایی به کاربر یا گروه
            bot.reply_to(message, completion.choices[0].message.content)

    except Exception as e:
        print(f"Error: {e}")

# روشن نگه داشتن ربات
print(f"Bot @{BOT_USERNAME} is running on Groq...")
bot.infinity_polling()
