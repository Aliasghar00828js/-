Import telebot
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
WEBHOOK_URL = "https://Lucid-vibrancy-production.app.railway.app" # آدرس سرور تو

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

jokes = load_json('jokes.json', [{"q": "خطا", "a": "دوباره تلاش کنید"}])
riddles = load_json('riddles.json', [{"q": "خطا", "a": "دوباره تلاش کنید"}])
truth_questions = load_json('truth.json', [{"q": "سوال حقیقتی یافت نشد!"}])
dare_questions = load_json('dare.json', [{"q": "سوال جراتی یافت نشد!"}])

# ==========================================
# بخش سوم: هندلر دستور استارت (منوی اصلی)
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    total_jokes = len(jokes)
    total_riddles = len(riddles)
    user_name = message.from_user.first_name 
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("😂 یه جوک بگو", "🧐 چیستان")
    markup.add("🎡 جرات یا حقیقت", "🧠 تست واکنش")
    markup.add("📩 پیشنهاد", "👨‍💻 پشتیبانی")
    
    welcome_text = (
        f"🌟 به ربات سرگرمی ما خوش اومدی {user_name} عزیز!\n\n"
        f"ما اینجا بیش از {total_jokes} جوک و {total_riddles} چیستان داریم.\n\n"
        f"📌 قابلیت‌ها:\n"
        f"✅ آرشیو جوک و چیستان‌های خنده‌دار\n"
        f"✅ بازی چالش‌برانگیز جرات یا حقیقت 🎡\n"
        f"✅ تست تمرکز و سرعت واکنش 🧠\n"
        f"✅ ارتباط مستقیم با تیم مدیریت\n\n"
        f"از منوی زیر یک گزینه رو انتخاب کن 👇"
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
        markup.add(types.InlineKeyboardButton("حقیقت 📖", callback_data="game_truth"),
                   types.InlineKeyboardButton("جرات 🚀", callback_data="game_dare"))
        bot.send_message(message.chat.id, "یکی رو انتخاب کن تا چرخ شانس بچرخه! 🎡", reply_markup=markup)

    elif message.text == "🧠 تست واکنش":
        text = "🎯 توی ذهنت بشمار و روی ثانیه ۸ دکمه توقف رو بزن!"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🚀 شروع بازی", callback_data="reaction_start"))
        bot.send_message(message.chat.id, text, reply_markup=markup)
        
    elif message.text == "👨‍💻 پشتیبانی":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("ارتباط با ادمین 💬", url="https://t.me/ALiasghR4321"))
        bot.send_message(message.chat.id, "برای پشتیبانی کلیک کنید:", reply_markup=markup)
        
    elif message.text == "📩 پیشنهاد":
        msg = bot.send_message(message.chat.id, "📝 لطفاً پیام یا پیشنهاد خود را بنویسید:")
        bot.register_next_step_handler(msg, forward_to_admin)

# ==========================================
# بخش پنجم: ارسال هوشمند پیشنهاد به ادمین
# ==========================================
def forward_to_admin(message):
    # جلوگیری از ارسال دکمه‌های منو به عنوان پیشنهاد
    main_buttons = ["😂 یه جوک بگو", "🧐 چیستان", "🎡 جرات یا حقیقت", "🧠 تست واکنش", "👨‍💻 پشتیبانی", "📩 پیشنهاد", "/start"]
    
    if message.text in main_buttons:
        bot.send_message(message.chat.id, "❌ ارسال پیشنهاد لغو شد.")
        handle_message(message) # اجرای دستور دکمه کلیک شده
        return

    try:
        # تنظیم زمان و تاریخ شمسی
        tehran_tz = pytz.timezone('Asia/Tehran')
        now = datetime.datetime.now(tehran_tz)
        jalali_now = jdatetime.datetime.fromgregorian(datetime=now)
        
        date_str = jalali_now.strftime("%Y/%m/%d")
        time_str = jalali_now.strftime("%H:%M:%S")
        user_id = message.from_user.id
        username = f"@{message.from_user.username}" if message.from_user.username else "ندارد"

        report = (
            f"📬 **پیشنهاد جدید دریافت شد**\n\n"
            f"👤 فرستنده: {message.from_user.first_name}\n"
            f"🆔 آیدی عددی: `{user_id}`\n"
            f"🔗 یوزرنیم: {username}\n"
            f"📅 تاریخ: `{date_str}`\n"
            f"⏰ ساعت: `{time_str}`\n\n"
            f"📝 **متن پیام:**\n{message.text}"
        )
        
        bot.send_message(ADMIN_CHAT_ID, report, parse_mode="Markdown")
        bot.send_message(message.chat.id, "✅ پیام شما با موفقیت برای برنامه‌نویس ارسال شد.")
    except Exception as e:
        bot.send_message(message.chat.id, "❌ مشکلی در ارسال رخ داد.")

# ==========================================
# بخش ششم: مدیریت Callback (دکمه‌های شیشه‌ای)
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    if call.data.startswith('ans_'):
        idx = int(call.data.split('_')[1])
        bot.send_message(call.message.chat.id, f"✅ پاسخ: {jokes[idx]['a']}")
        bot.answer_callback_query(call.id)

    elif call.data.startswith('game_'):
        bot.edit_message_text("🎡 در حال چرخاندن چرخ شانس...", call.message.chat.id, call.message.message_id)
        time.sleep(1)
        q_list = truth_questions if call.data == "game_truth" else dare_questions
        q = random.choice(q_list)["q"]
        emoji = "📖" if call.data == "game_truth" else "🚀"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔄 یکی دیگه", callback_data=call.data))
        bot.edit_message_text(f"{emoji} **سوال:**\n\n{q}", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

    elif call.data == "reaction_start":
        user_timers[call.from_user.id] = time.time()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🛑 توقف تایمر", callback_data="reaction_stop"))
        bot.edit_message_text("⏱ توی ذهنت بشمار... وقتی به ۸ ثانیه رسیدی توقف رو بزن!", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "reaction_stop":
        if call.from_user.id in user_timers:
            elapsed = time.time() - user_timers[call.from_user.id]
            del user_timers[call.from_user.id]
            bot.edit_message_text(f"⏱ زمان شما: `{elapsed:.2f}` ثانیه\nاختلاف با ۸ ثانیه: `{abs(8-elapsed):.2f}`", call.message.chat.id, call.message.message_id, parse_mode="Markdown")

# ==========================================
# اجرای نهایی
# ==========================================
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
