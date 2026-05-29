import telebot
import random
from telebot import types
import os
import datetime
import pytz
import jdatetime
from flask import Flask
from threading import Thread

# --- تنظیمات وب‌سرور ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# --- تنظیمات اولیه ---
TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = 7007467756  
bot = telebot.TeleBot(TOKEN)

# --- لیست جوک‌ها ---
jokes = [
    {"q": "میدونی اگه به بتن دست بزنی چی میگه؟", "a": "میگه نتن! 😂"},
    {"q": "میدونی ریاضی دان ها وقتی میرن دسشویی چیکار میکنن؟", "a": "ππ میکنن ها ها ها! 🤣"},
    {"q": "میدونی به دینی که هنوز نیومده چی میگن؟", "a": "بتادین! 💊"},
    {"q": "نوشابه با دوغ دعواش میشه، چی میگه؟", "a": "میگه برووو برووو تا نزدم پونه‌تو پاره کنم! 🥛"},
    {"q": "میدونی به کسی که خواهرش رزمی کاره چی میگن؟", "a": "خوارزمی! 🥋"},
    {"q": "میدونی چرا ماهی ها باهم ازدواج نمی کنن؟", "a": "چون پولکین! 🐟"},
    {"q": "میدونی اگه شیرینی فروشی آتیش بگیره چی میشه؟", "a": "تر و خشک باهم میسوزن! 🍰"},
    {"q": "میدونی به پشت تن ماهی چی میگن؟", "a": "میگن تنبک! 🥁"},
    {"q": "سیب زمینیا دعواشون بشه چیکار میکنن؟", "a": "میزنن همو پوره میکنن! 🥔"},
    {"q": "میدونی میوه ها موقع تولد چی کادو میدن؟", "a": "آواکادو! 🥑"}
]

# --- هندلر استارت ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("😂 یه جوک بگو")
    markup.add("📩 پیشنهادات و انتقادات", "👨‍💻 پشتیبانی")
    bot.send_message(message.chat.id, "سلام! خوش اومدی. از دکمه‌های زیر استفاده کن:", reply_markup=markup)

# --- مدیریت پیام‌ها ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == "😂 یه جوک بگو":
        joke = random.choice(jokes)
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("میدونی چرا؟ 🤔", callback_data=f"ans_{jokes.index(joke)}")
        markup.add(btn)
        bot.send_message(message.chat.id, joke["q"], reply_markup=markup)
        
    elif message.text == "👨‍💻 پشتیبانی":
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("ارتباط با ادمین 💬", url="https://t.me/ALiasghR4321")
        markup.add(btn)
        bot.send_message(message.chat.id, "برای پشتیبانی روی دکمه کلیک کن:", reply_markup=markup)
        
    elif message.text == "📩 پیشنهادات و انتقادات":
        msg = bot.send_message(message.chat.id, "📝 پیام یا پیشنهاد خود را بنویس.\nبرای انصراف بنویس: انصراف")
        bot.register_next_step_handler(msg, forward_to_admin)

# --- ارسال به ادمین ---
def forward_to_admin(message):
    if message.text == "انصراف":
        bot.send_message(message.chat.id, "❌ عملیات لغو شد.")
        return

    try:
        tehran_tz = pytz.timezone('Asia/Tehran')
        now = datetime.datetime.now(tehran_tz)
        jalali_now = jdatetime.datetime.fromgregorian(datetime=now)
        
        report = f"📬 پیام جدید:\n👤 کاربر: @{message.from_user.username}\n📅 تاریخ: {jalali_now.strftime('%Y/%m/%d - %H:%M:%S')}\n\n📝 متن: {message.text}"
        bot.send_message(ADMIN_CHAT_ID, report)
        bot.send_message(message.chat.id, "✅ با موفقیت ارسال شد.")
    except:
        bot.send_message(message.chat.id, "❌ خطا در ارسال.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('ans_'))
def answer_joke(call):
    idx = int(call.data.split('_')[1])
    bot.send_message(call.message.chat.id, jokes[idx]["a"])

if __name__ == "__main__":
    bot.polling(none_stop=True)
    
