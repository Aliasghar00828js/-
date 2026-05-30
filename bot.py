import telebot
import random
from telebot import types
import os
import datetime
import pytz
import jdatetime
import json
from flask import Flask
from threading import Thread

# --- تنظیمات وب‌سرور برای جلوگیری از خواب رفتن ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Online!"

def run():
    # دریافت پورت خودکار از سرور Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# اجرای سرور نگهدارنده قبل از شروع ربات
keep_alive()

# --- تنظیمات اولیه ربات ---
TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = 7007467756  

bot = telebot.TeleBot(TOKEN)

# --- خواندن لیست جوک‌ها از فایل JSON ---
try:
    with open('jokes.json', 'r', encoding='utf-8') as f:
        jokes = json.load(f)
except Exception as e:
    # در صورتی که فایل پیدا نشد یا مشکلی داشت
    jokes = [{"q": "خطا در خواندن جوک‌ها", "a": "لطفاً به ادمین اطلاع دهید."}]

# --- خواندن لیست چیستان‌ها از فایل JSON ---
try:
    with open('riddles.json', 'r', encoding='utf-8') as f:
        riddles = json.load(f)
except Exception as e:
    # در صورتی که فایل پیدا نشد یا مشکلی داشت
    riddles = [{"q": "خطا در خواندن چیستان‌ها", "a": "لطفاً به ادمین اطلاع دهید."}]

# --- هندلر دستور استارت ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    total_jokes = len(jokes)
    total_riddles = len(riddles)
    user_first_name = message.from_user.first_name 
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("😂 یه جوک بگو")
    btn_chiestan = types.KeyboardButton("🧐 چیستان") # دکمه جدید
    btn2 = types.KeyboardButton("📩 پیشنهادات و انتقادات")
    btn3 = types.KeyboardButton("👨‍💻 پشتیبانی")
    
    markup.add(btn1, btn_chiestan) # قرار دادن جوک و چیستان در یک ردیف
    markup.add(btn2, btn3)
    
    welcome_text = (
        f"🌟 به ربات جوک‌های بی‌مزه خوش اومدی {user_first_name} عزیز!\n\n"
        f"ما اینجا بیش از {total_jokes} جوک و {total_riddles} چیستان آماده کردیم.\n\n"
        f"📌 قابلیت‌ها:\n"
        f"✅ آرشیو بزرگ جوک (+{total_jokes} مورد)\n"
        f"✅ آرشیو جذاب چیستان (+{total_riddles} مورد)\n"
        f"✅ ارسال مستقیم پیشنهادات به ادمین\n"
        f"✅ پشتیبانی آنلاین\n\n"
        f"از منوی زیر استفاده کن 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# --- مدیریت دکمه‌های متنی ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == "😂 یه جوک بگو":
        joke = random.choice(jokes)
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("میدونی چرا؟ 🤔", callback_data=f"ans_{jokes.index(joke)}")
        markup.add(btn)
        bot.send_message(message.chat.id, joke["q"], reply_markup=markup)

    elif message.text == "🧐 چیستان": 
        riddle = random.choice(riddles)
        # استفاده از تگ اسپویلر در HTML برای مخفی کردن پاسخ
        riddle_text = f"❓ {riddle['q']}\n\nپاسخ: <tg-spoiler>{riddle['a']}</tg-spoiler>"
        bot.send_message(message.chat.id, riddle_text, parse_mode="HTML")
        
    elif message.text == "👨‍💻 پشتیبانی":
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("ارتباط مستقیم با ادمین 💬", url="https://t.me/ALiasghR4321")
        markup.add(btn)
        bot.send_message(message.chat.id, "برای ارتباط با پشتیبانی روی دکمه زیر کلیک کنید:", reply_markup=markup)
        
    elif message.text == "📩 پیشنهادات و انتقادات":
        msg = bot.send_message(message.chat.id, "📝 لطفاً پیام، پیشنهاد یا جوک خود را همراه با نامتان ارسال کنید.\n\n⚠️ پیام شما مستقیماً برای برنامه‌نویس فوروارد می‌شود. 👨‍💻")
        bot.register_next_step_handler(msg, forward_to_admin)

# --- ارسال پیشنهاد به ادمین ---
def forward_to_admin(message):
    if message.text in ["😂 یه جوک بگو", "🧐 چیستان", "👨‍💻 پشتیبانی", "📩 پیشنهادات و انتقادات", "/start"]:
        bot.send_message(message.chat.id, "❌ ارسال پیشنهاد لغو شد.")
        handle_message(message)
        return

    try:
        tehran_tz = pytz.timezone('Asia/Tehran')
        now = datetime.datetime.now(tehran_tz)
        jalali_now = jdatetime.datetime.fromgregorian(datetime=now)
        date_str = jalali_now.strftime("%Y/%m/%d")
        time_str = jalali_now.strftime("%H:%M:%S")

        user_id = message.from_user.id
        username = f"@{message.from_user.username}" if message.from_user.username else "ندارد"

        report_text = (
            f"📬 **پیشنهاد / پیام جدید**\n\n"
            f"👤 **آیدی عددی:** `{user_id}`\n"
            f"🔗 **یوزرنیم:** {username}\n"
            f"📅 **تاریخ:** {date_str}\n"
            f"⏰ **ساعت (تهران):** {time_str}\n\n"
        )

        if message.text:
            report_text += f"📝 **متن پیام:**\n{message.text}"
            bot.send_message(ADMIN_CHAT_ID, report_text, parse_mode="Markdown")
        else:
            report_text += f"📎 **کاربر یک فایل/عکس ارسال کرده است**"
            bot.send_message(ADMIN_CHAT_ID, report_text, parse_mode="Markdown")
            bot.copy_message(ADMIN_CHAT_ID, message.chat.id, message.message_id)

        bot.send_message(message.chat.id, "✅ پیام شما با موفقیت برای برنامه‌نویس ارسال شد. ممنون!")
    except Exception as e:
        bot.send_message(message.chat.id, "❌ خطایی در ارسال رخ داد.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('ans_'))
def answer_joke(call):
    idx = int(call.data.split('_')[1])
    bot.send_message(call.message.chat.id, jokes[idx]["a"])
    bot.answer_callback_query(call.id)

# شروع به کار ربات
if __name__ == "__main__":
    bot.polling(none_stop=True)
    
