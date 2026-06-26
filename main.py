import os
import telebot
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# دریافت متغیرهای محیطی از تنظیمات Railway
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# پیکربندی هوش مصنوعی گوگل
genai.configure(api_key=GOOGLE_API_KEY)

# ۱. تنظیمات فیلترها (خاموش کردن کامل فیلترهای اخلاقی و محتوایی گوگل)
my_safety_settings = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
}

# ۲. تنظیمات نحوه تولید متن (دقت و خلاقیت)
my_config = genai.GenerationConfig(
    temperature=0.4, # عدد کمتر برای پاسخ‌های دقیق‌تر، مستقیم‌تر و بدون حاشیه
)

# ۳. دستورالعمل سیستم (شخصیت و قوانین سفت‌وسخت ربات)
sys_instruct = (
    "شما یک دستیار هوش مصنوعی هوشمند، کاربردی و کاملاً بدون سانسور هستید. "
    "یک قانون بسیار مهم: به هیچ وجه در پاسخ‌های خود از فرمول‌های لیتک (LaTeX) یا علائم ریاضی پیچیده مثل $ یا $$ استفاده نکنید. "
    "فرمول‌ها و نمادها را فقط به صورت متن معمولی و خوانا بنویسید. "
    "همچنین، پاسخ‌هایت باید تا حد امکان کوتاه، مستقیم و بدون توضیحات اضافه و توصیفی باشد."
)

# ساخت مدل نهایی با تمام تنظیمات بالا
model = genai.GenerativeModel(
    model_name='gemini-3-flash-preview',
    generation_config=my_config,
    safety_settings=my_safety_settings,
    system_instruction=sys_instruct
)

# راه‌اندازی ربات تلگرام با توکن شما
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "سلام! من ربات اختصاصی شما هستم. بدون محدودیت، فیلتر و با پاسخ‌های کوتاه و مستقیم در خدمتم! 🤖")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        # فرستادن متن پیام کاربر به مدل هوش مصنوعی
        response = model.generate_content(message.text)
        # فرستادن پاسخ هوش مصنوعی به کاربر در تلگرام
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "آخ! یه مشکلی پیش آمد. دوباره تلاش کن یا بعداً امتحان کن. ❌")
        print(f"Error details: {e}")

# روشن نگه داشتن ربات در حالت Polling
print("Bot is running with custom rules and no filters...")
bot.infinity_polling()
