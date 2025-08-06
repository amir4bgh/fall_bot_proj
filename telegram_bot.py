import random
import json
import os
import logging
from datetime import datetime, date
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# تنظیم لاگینگ برای دیباگ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# گرفتن توکن از متغیر محیطی
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("توکن ربات پیدا نشد! لطفاً متغیر محیطی TOKEN را تنظیم کنید.")

# لیست جملات الهام‌بخش
SENTENCES = [
    "امروز کمی استراحت کن و به خودت اهمیت بده.",
    "امروز موقع رد شدن از خیابون حواست باشه!",
    "امروز به مامانت کمک کن، یه کار کوچیک می‌تونه روزش رو قشنگ‌تر کنه.",
    "امروز یه هدف کوچیک برای خودت بذار و بهش برس.",
    "امروز با یه دوست قدیمی تماس بگیر و حالش رو بپرس.",
    "امروز یه کار جدید امتحان کن، شاید عاشقش شدی!",
]

# مسیر فایل JSON برای ذخیره داده‌ها
DATA_FILE = "user_requests.json"

# تابع برای بارگذاری داده‌ها از فایل JSON
def load_user_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        logger.warning("فایل JSON پیدا نشد یا خراب است. فایل جدید ایجاد می‌شود.")
        return {}

# تابع برای ذخیره داده‌ها در فایل JSON
def save_user_data(data):
    try:
        with open(DATA_FILE, "w") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"خطا در ذخیره فایل JSON: {e}")

# تابع برای دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_name = update.message.from_user.first_name or "دوست عزیز"
        welcome_message = (
            f"سلام {user_name}! 😊\n"
            "من ربات فال روزانه‌ام. هر روز یه جمله‌ی راهنما برات دارم که می‌تونه روزت رو قشنگ‌تر کنه!\n"
            "برای گرفتن فال امروزت، /daily رو بزن."
        )
        await update.message.reply_text(welcome_message)
    except Exception as e:
        logger.error(f"خطا در دستور /start: {e}")
        await update.message.reply_text("اوپس! یه مشکلی پیش اومد. دوباره امتحان کن.")

# تابع برای دستور /daily
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.message.from_user.id)
        user_name = update.message.from_user.first_name or "دوست عزیز"
        today = date.today().isoformat()

        # بارگذاری داده‌های کاربران
        user_data = load_user_data()

        # بررسی محدودیت روزانه
        if user_id in user_data and user_data[user_id]["last_request_date"] == today:
            await update.message.reply_text(
                f"{user_name} عزیز، تو امروز فالت رو گرفتی! 😊\n"
                "امیدوارم به اون جمله خوب عمل کنی. فردا دوباره برگرد پیشمون!"
            )
            return

        # انتخاب جمله تصادفی
        random_sentence = random.choice(SENTENCES)

        # ذخیره درخواست کاربر
        user_data[user_id] = {"last_request_date": today}
        save_user_data(user_data)

        # ارسال جمله و پیام دوستانه
        await update.message.reply_text(
            f"فال امروز تو، {user_name}:\n{random_sentence}\n\n"
            "امیدوارم این جمله روزت رو بهتر کنه! فردا دوباره منتظرتیم، دوست عزیز! 😊"
        )
    except Exception as e:
        logger.error(f"خطا در دستور /daily: {e}")
        await update.message.reply_text("اوپس! یه مشکلی پیش اومد. دوباره امتحان کن.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت خطاهای ربات"""
    logger.error(f"خطا رخ داد: {context.error}")
    if update and update.message:
        await update.message.reply_text("متأسفم، یه خطایی پیش اومد. لطفاً دوباره امتحان کن.")

def main():
    try:
        # ساخت اپلیکیشن ربات
        application = Application.builder().token(TOKEN).build()

        # اضافه کردن هندلرها
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("daily", daily))

        # اضافه کردن هندلر خطاها
        application.add_error_handler(error_handler)

        # شروع ربات
        logger.info("ربات شروع شد...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"خطا در راه‌اندازی ربات: {e}")
        raise

if __name__ == "__main__":
    main()