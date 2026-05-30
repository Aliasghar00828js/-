import telebot
import random
import time
from telebot import types
import os
import datetime
import pytz
import jdatetime
import json
from flask import Flask, request

# ==========================================
# بخش اول: تنظیمات اولیه و Webhook
# ==========================================
TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = 7007467756  
WEBHOOK_URL = "https://Lucid-vibrancy-production.up.railway.app"

bot = telebot.TeleBot(TOKEN)
user_timers = {} 

app = Flask('')

@app.route('/')
def home():
    return "Bot is Online!"

@app.route('/' + TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# ==========================================
# بخش دوم: خواندن داده‌ها از فایل‌های JSON
# ==========================================
def load_json(filename, default_data):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default_data

# بارگذاری همه فایل‌ها
jokes = load_json('jokes.json', [{"q": "خطا در بارگذاری", "a": "ادمین را باخبر کنید"}])
riddles = load_json('riddles.json', [{"q": "خطا در بارگذاری", "a": "ادمین را باخبر کنید"}])
truth_questions = load_json('truth.json', [{"q": "سوال حقیقتی یافت نشد!"}])
dare_questions = load_json('dare.json', [{"q": "سوال جراتی یافت نشد!"}])

# ==========================================
# بخش سوم: هندلر دستور استارت (منوی اصلی)
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_first_name = message.from_user.first_name 
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_joke = types.KeyboardButton("😂 یه جوک بگو")
    btn_riddle = types.KeyboardButton("🧐 چیستان")
    btn_game = types.KeyboardButton("🎡 جرات یا حقیقت") # دکمه جدید
    btn_reaction = types.KeyboardButton("🧠 تست واکنش")
    btn_support = types.KeyboardButton("👨‍💻 پشتیبانی")
    btn_suggest = types.KeyboardButton("📩 پیشنهاد")
    
    markup.add(btn_joke, btn_riddle)
    markup.add(btn_game, btn_reaction)
    markup.add(btn_suggest, btn_support)
    
    welcome_text = (
        f"🌟 سلام {user_first_name} عزیز!\n"
        f"به ربات سرگرمی خوش اومدی.\n\n"
        f"از منوی زیر بازی مورد علاقه‌ت رو انتخاب کن 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# ==========================================
# بخش چهارم: مدیریت دکمه‌های متنی
# ==========================================
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
        riddle_text = f"❓ {riddle['q']}\n\nپاسخ: <tg-spoiler>{riddle['a']}</tg-spoiler>"
        bot.send_message(message.chat.id, riddle_text, parse_mode="HTML")
        
    elif message.text == "🎡 جرات یا حقیقت":
        markup = types.InlineKeyboardMarkup()
        btn_t = types.InlineKeyboardButton("حقیقت 📖", callback_data="game_truth")
        btn_d = types.InlineKeyboardButton("جرات 🚀", callback_data="game_dare")
        markup.add(btn_t, btn_d)
        bot.send_message(message.chat.id, "یکی رو انتخاب کن تا چرخ شانس بچرخه! 🎡", reply_markup=markup)

    elif message.text == "🧠 تست واکنش":
        text = "🎯 روی ثانیه ۸ دکمه توقف رو بزن!"
        markup = types.InlineKeyboardMarkup()
        btn_start = types.InlineKeyboardButton("🚀 شروع", callback_data="reaction_start")
        markup.add(btn_start)
        bot.send_message(message.chat.id, text, reply_markup=markup)
        
    elif message.text == "👨‍💻 پشتیبانی":
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("ارتباط با ادمین 💬", url="https://t.me/ALiasghR4321")
        markup.add(btn)
        bot.send_message(message.chat.id, "برای پشتیبانی کلیک کنید:", reply_markup=markup)
        
    elif message.text == "📩 پیشنهاد":
        msg = bot.send_message(message.chat.id, "📝 پیام خود را بنویسید:")
        bot.register_next_step_handler(msg, forward_to_admin)

# ==========================================
# بخش پنجم: مدیریت کلیک‌های اینلاین (Callback)
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    # ۱. هندلر جوک
    if call.data.startswith('ans_'):
        idx = int(call.data.split('_')[1])
        bot.send_message(call.message.chat.id, jokes[idx]["a"])
        bot.answer_callback_query(call.id)

    # ۲. هندلر جرات یا حقیقت
    elif call.data.startswith('game_'):
        if call.data == "game_truth":
            q = random.choice(truth_questions)["q"]
            title = "📖 **حقیقت:**"
        else:
            q = random.choice(dare_questions)["q"]
            title = "🚀 **جرات (شجاعت):**"
        
        # افکت چرخش چرخ شانس
        bot.edit_message_text("🎡 در حال چرخاندن چرخ شانس...", call.message.chat.id, call.message.message_id)
        time.sleep(1) # وقفه برای جذابیت
        
        final_text = f"{title}\n\n{q}"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔄 یکی دیگه", callback_data=call.data))
        bot.edit_message_text(final_text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    # ۳. هندلر تست واکنش (خلاصه شده برای جلوگیری از شلوغی)
    elif call.data == "reaction_start":
        user_timers[call.from_user.id] = time.time()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🛑 توقف", callback_data="reaction_stop"))
        bot.edit_message_text("⏱ بشمار و توقف رو بزن...", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "reaction_stop":
        if call.from_user.id in user_timers:
            elapsed = time.time() - user_timers[call.from_user.id]
            del user_timers[call.from_user.id]
            bot.edit_message_text(f"⏱ زمان شما: {elapsed:.2f} ثانیه", call.message.chat.id, call.message.message_id)

# ==========================================
# بخش ششم: توابع کمکی (ارسال به ادمین)
# ==========================================
def forward_to_admin(message):
    try:
        report = f"📩 پیام جدید از `{message.from_user.id}`:\n\n{message.text}"
        bot.send_message(ADMIN_CHAT_ID, report, parse_mode="Markdown")
        bot.send_message(message.chat.id, "✅ ارسال شد!")
    except:
        bot.send_message(message.chat.id, "❌ خطا در ارسال.")

# ==========================================
# اجرای نهایی
# ==========================================
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
    
