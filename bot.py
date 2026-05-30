import telebot
import random
import time  # برای محاسبه زمان در تست واکنش
from telebot import types
import os
import datetime
import pytz
import jdatetime
import json
from flask import Flask, request  # ابزار request برای گرفتن اطلاعات از تلگرام اضافه شد

# ==========================================
# بخش اول: تنظیمات اولیه و آدرس سرور تو در Railway
# ==========================================
TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = 7007467756  

# آدرس اختصاصی سرور تو در ری‌لووی (بدون اسلش / در انتها)
WEBHOOK_URL = "https://Lucid-vibrancy-production.up.railway.app"

bot = telebot.TeleBot(TOKEN)

# متغیر حافظه برای بازی تست واکنش
user_timers = {} 

# ==========================================
# بخش دوم: تنظیمات وب‌سرور Flask و مسیرهای ورودی
# ==========================================
app = Flask('')

# صفحه اصلی که خودت بازش می‌کردی و می‌نوشت Bot is Online
@app.route('/')
def home():
    return "Bot is Online!"

# این مسیر مخصوص تلگرام است؛ تلگرام پیام‌ها را به این آدرسِ مخفی پست (POST) می‌کند
@app.route('/' + TOKEN, methods=['POST'])
def get_message():
    # ۱. دریافت اطلاعات خام از تلگرام
    json_string = request.get_data().decode('utf-8')
    # ۲. تبدیل اطلاعات خام به فرمت قابل فهم برای ربات
    update = telebot.types.Update.de_json(json_string)
    # ۳. سپردن پیام به ربات برای پردازش
    bot.process_new_updates([update])
    return "!", 200

# ==========================================
# بخش سوم: خواندن داده‌ها از فایل‌های JSON
# ==========================================
try:
    with open('jokes.json', 'r', encoding='utf-8') as f:
        jokes = json.load(f)
except Exception as e:
    jokes = [{"q": "خطا در خواندن جوک‌ها", "a": "لطفاً به ادمین اطلاع دهید."}]

try:
    with open('riddles.json', 'r', encoding='utf-8') as f:
        riddles = json.load(f)
except Exception as e:
    riddles = [{"q": "خطا در خواندن چیستان‌ها", "a": "لطفاً به ادمین اطلاع دهید."}]

# ==========================================
# بخش چهارم: هندلر دستور استارت (منوی اصلی)
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    total_jokes = len(jokes)
    total_riddles = len(riddles)
    user_first_name = message.from_user.first_name 
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("😂 یه جوک بگو")
    btn_chiestan = types.KeyboardButton("🧐 چیستان")
    btn_reaction = types.KeyboardButton("🧠 تست واکنش و هوش")
    btn2 = types.KeyboardButton("📩 پیشنهادات و انتقادات")
    btn3 = types.KeyboardButton("👨‍💻 پشتیبانی")
    
    markup.add(btn1, btn_chiestan)
    markup.add(btn_reaction)
    markup.add(btn2, btn3)
    
    welcome_text = (
        f"🌟 به ربات سرگرمی ما خوش اومدی {user_first_name} عزیز!\n\n"
        f"ما اینجا بیش از {total_jokes} جوک و {total_riddles} چیستان داریم.\n\n"
        f"📌 قابلیت‌ها:\n"
        f"✅ آرشیو جوک و چیستان\n"
        f"✅ چالش تست تمرکز و IQ 🧠\n"
        f"✅ ارتباط مستقیم با ادمین\n\n"
        f"از منوی زیر یک گزینه رو انتخاب کن 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# ==========================================
# بخش پنجم: مدیریت کلیک روی دکمه‌های متنی کیبورد
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
        
    elif message.text == "🧠 تست واکنش و هوش":
        text = (
            "🎯 **تست تمرکز و سرعت واکنش (IQ)**\n\n"
            "طرز کار این بخش به این صورته:\n"
            "وقتی دکمه شروع رو بزنی، تایمر تو پس‌زمینه شروع به شمردن می‌کنه.\n"
            "تو باید توی ذهنت بشماری و **دقیقاً روی ثانیه ۸** دکمه توقف رو بزنی!\n\n"
            "🏆 **رتبه‌بندی:**\n"
            "🥇 اختلاف کمتر از ۰.۲ ثانیه: نابغه!\n"
            "🥈 اختلاف کمتر از ۰.۵ ثانیه: تمرکز عالی!\n"
            "🥉 اختلاف کمتر از ۱ ثانیه: خوب و نرمال\n"
            "🐢 بیشتر از ۱ ثانیه: نیاز به تمرین بیشتر!\n\n"
            "آماده‌ای؟"
        )
        markup = types.InlineKeyboardMarkup()
        btn_start = types.InlineKeyboardButton("🚀 شروع بازی", callback_data="reaction_start")
        btn_cancel = types.InlineKeyboardButton("❌ انصراف", callback_data="reaction_cancel")
        markup.add(btn_start, btn_cancel)
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup)
        
    elif message.text == "👨‍💻 پشتیبانی":
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("ارتباط مستقیم با ادمین 💬", url="https://t.me/ALiasghR4321")
        markup.add(btn)
        bot.send_message(message.chat.id, "برای ارتباط با پشتیبانی روی دکمه زیر کلیک کنید:", reply_markup=markup)
        
    elif message.text == "📩 پیشنهادات و انتقادات":
        msg = bot.send_message(message.chat.id, "📝 لطفاً پیام، پیشنهاد یا جوک خود را ارسال کنید.\n\n⚠️ پیام شما مستقیماً برای برنامه‌نویس فوروارد می‌شود.")
        bot.register_next_step_handler(msg, forward_to_admin)

# ==========================================
# بخش ششم: ارسال پیشنهاد به ادمین
# ==========================================
def forward_to_admin(message):
    if message.text in ["😂 یه جوک بگو", "🧐 چیستان", "🧠 تست واکنش و هوش", "👨‍💻 پشتیبانی", "📩 پیشنهادات و انتقادات", "/start"]:
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
            f"⏰ **ساعت:** {time_str}\n\n"
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

# ==========================================
# بخش هفتم: مدیریت دکمه‌های شیشه‌ای (Inline Buttons)
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data.startswith('ans_'))
def answer_joke(call):
    idx = int(call.data.split('_')[1])
    bot.send_message(call.message.chat.id, jokes[idx]["a"])
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('reaction_'))
def handle_reaction_game(call):
    user_id = call.from_user.id

    if call.data == "reaction_cancel":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "❌ به منوی اصلی برگشتیم.")

    elif call.data == "reaction_start":
        user_timers[user_id] = time.time()
        markup = types.InlineKeyboardMarkup()
        btn_stop = types.InlineKeyboardButton("🛑 توقف تایمر", callback_data="reaction_stop")
        btn_back = types.InlineKeyboardButton("🔙 انصراف", callback_data="reaction_cancel")
        markup.add(btn_stop)
        markup.add(btn_back)
        
        bot.edit_message_text(
            "⏱ **تایمر شروع شد!**\n\nتوی ذهنت بشمار و **دقیقاً بعد از ۸ ثانیه** دکمه توقف رو بزن...",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )

    elif call.data == "reaction_stop":
        if user_id in user_timers:
            end_time = time.time() 
            elapsed = end_time - user_timers[user_id] 
            del user_timers[user_id] 
            
            diff = abs(8.0 - elapsed) 
            
            if diff <= 0.2:
                rank = "🥇 نابغه! تمرکزت فوق‌العاده‌ست!"
            elif diff <= 0.5:
                rank = "🥈 عالی! سرعت و دقتت خیلی خوبه!"
            elif diff <= 1.0:
                rank = "🥉 خوب و نرمال. می‌تونی بهترم بشی!"
            else:
                rank = "🐢 یکم بی‌دقتی کردی! نیاز به تمرین داری."

            text = (
                f"🎯 **نتیجه تست شما:**\n\n"
                f"⏱ زمان ثبت شده: `{elapsed:.2f}` ثانیه\n"
                f"📏 اختلاف با ۸ ثانیه: `{diff:.2f}` ثانیه\n\n"
                f"🧠 امتیاز شما: {rank}"
            )
            
            markup = types.InlineKeyboardMarkup()
            btn_retry = types.InlineKeyboardButton("🔄 دوباره بازی کن", callback_data="reaction_start")
            btn_main = types.InlineKeyboardButton("🔙 بازگشت به منو", callback_data="reaction_cancel")
            markup.add(btn_retry, btn_main)
            
            bot.edit_message_text(
                text,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="Markdown",
                reply_markup=markup
            )
        else:
            bot.answer_callback_query(call.id, "زمان شما ثبت نشده بود! دوباره شروع کنید.", show_alert=True)

# ==========================================
# بخش هشتم: فعال‌سازی وب‌هوک و اجرای سرور
# ==========================================
if __name__ == "__main__":
    # ۱. ابتدا هر اتصال وب‌هوک قدیمی را پاک می‌کنیم تا تداخل ایجاد نشود
    bot.remove_webhook()
    
    # ۲. آدرس جدید وب‌هوک را به تلگرام معرفی می‌کنیم (ترکیب لینک ری‌لووی و توکن ربات)
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    
    # ۳. روشن کردن سرور فلاسک روی پورت سرور ری‌لووی
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
        
