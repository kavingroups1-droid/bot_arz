import logging
import os
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "9278969559:AAFW3xpkcgYAKdJy31SCpa7DqIF1UtfJDcY"
SUPPORT_CONTACT = "+971544048575"
ORDER_FILE = "order_number.txt"
USERS_FILE = "users.txt"
ADMIN_USERNAME = "arzparss"
ADMIN_CHAT_ID_FILE = "admin_chat_id.txt"

PORT = int(os.environ.get("PORT", "10000"))
WEBHOOK_URL = "https://bot-arz.onrender.com"

def load_admin_chat_id():
    if os.path.exists(ADMIN_CHAT_ID_FILE):
        try:
            with open(ADMIN_CHAT_ID_FILE, "r", encoding="utf-8") as f:
                return int(f.read().strip())
        except Exception:
            return None
    return None

def save_admin_chat_id(chat_id):
    with open(ADMIN_CHAT_ID_FILE, "w", encoding="utf-8") as f:
        f.write(str(chat_id))

ADMIN_CHAT_ID = load_admin_chat_id()

def add_user(user_id):
    try:
        with open(USERS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{user_id}\n")
    except Exception as e:
        logging.error(f"Error saving user: {e}")

def load_users():
    if not os.path.exists(USERS_FILE):
        return set()
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except Exception as e:
        logging.error(f"Error loading users: {e}")
        return set()

def track_users_middleware(user_id):
    users = load_users()
    if str(user_id) not in users:
        add_user(user_id)

def get_next_order_number():
    if not os.path.exists(ORDER_FILE):
        current_number = 1149
    else:
        try:
            with open(ORDER_FILE, "r", encoding="utf-8") as f:
                current_number = int(f.read().strip())
        except Exception:
            current_number = 1149
            
    next_number = current_number + 1
    with open(ORDER_FILE, "w", encoding="utf-8") as f:
        f.write(str(next_number))
    return next_number

SOURCE_CURRENCY, TARGET_AMOUNT, CONTACT_INFO, ID_PHOTO, WAIT_PHOTO = range(5)

MAIN_MENU_KEYBOARD = [
    ['ثبت سفارش جدید'],
    ['نرخ لحظه‌ای', 'پیگیری سفارش'],
    ['ارتباط با ما', 'درباره ما']
]

def format_customer_header(user) -> str:
    if not user:
        return "👤 مشتری: نامشخص"
    full_name = user.full_name or "نامشخص"
    username = f"@{user.username}" if user.username else "ندارد"
    return f"👤 مشتری: {full_name}\n🆔 آیدی عددی: {user.id}\n🔗 یوزرنیم: {username}"

async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message or update.effective_message.text in [
        'ثبت سفارش جدید', 'نرخ لحظه‌ای', 'پیگیری سفارش', 'ارتباط با ما', 'درباره ما',
        'دلار آمریکا', 'تتر', 'درهم امارات', 'لیر ترکیه', 'پوند انگلیس', 'یورو', 'یوآن چین', 'ریال عمان', 'تومان (ایران)', 'انصراف و لغو'
    ]:
        return

    user_id = update.effective_user.id
    track_users_middleware(user_id)

    if ADMIN_CHAT_ID:
        try:
            header = format_customer_header(update.effective_user)
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"📩 پیام جدید:\n{header}")
            await context.bot.forward_message(chat_id=ADMIN_CHAT_ID, from_chat_id=update.effective_chat.id, message_id=update.effective_message.message_id)
        except Exception as e:
            logging.error(f"Error forwarding message: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    track_users_middleware(user.id)
    
    if user and user.username and user.username.lower() == ADMIN_USERNAME.lower():
        save_admin_chat_id(update.effective_chat.id)
        global ADMIN_CHAT_ID
        ADMIN_CHAT_ID = update.effective_chat.id
        await update.message.reply_text(
            f"✅ سلام ادمین عزیز! آیدی عددی شما ({update.effective_chat.id}) ثبت شد.\n"
            "از این پس تمام سفارش‌ها، مدارک و پیام‌های مشتریان به همین چت ارسال می‌شود.",
            reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True)
        )
        return

    await update.message.reply_text(
        'به صرافی خوش آمدید. لطفاً از منوی زیر گزینه مورد نظر خود را انتخاب کنید:',
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True)
    )

async def live_rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_users_middleware(update.effective_user.id)
    await update.message.reply_text(
        '📈 استعلام نرخ لحظه‌ای\n\n'
        'با توجه به نوسانات دقیقه‌ای بازار، جهت دریافت دقیق‌ترین نرخ‌ها لطفاً به شماره واتس‌اپ ما پیام دهید:\n'
        f'{SUPPORT_CONTACT}'
    )

async def track_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_users_middleware(update.effective_user.id)
    await update.message.reply_text(
        '🔍 پیگیری سفارش\n\n'
        'برای پیگیری وضعیت سفارش خود، لطفاً شماره پیگیری یا نام خود را به پشتیبانی تلگرام یا واتس‌اپ ما ارسال نمایید:\n'
        f'{SUPPORT_CONTACT}'
    )

async def contact_us(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_users_middleware(update.effective_user.id)
    await update.message.reply_text(
        '📞 ارتباط با ما و راهنما\n\n'
        'پشتیبانی ۲۴ ساعته و واتس‌اپ:\n'
        f'{SUPPORT_CONTACT}\n\n'
        'پاسخگوی به سوالات شما هستیم.'
    )

async def about_us(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_users_middleware(update.effective_user.id)
    await update.message.reply_text(
        '🏢 درباره ما\n\n'
        'صرافی ما با سال‌ها تجربه درخشان در زمینه حواله‌جات ارزی، امن‌ترین و سریع‌ترین خدمات را با بهترین نرخ به شما ارائه می‌دهد.'
    )

async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_users_middleware(update.effective_user.id)
    currencies = [
        ['دلار آمریکا', 'تتر'],
        ['درهم امارات', 'لیر ترکیه'],
        ['پوند انگلیس', 'یورو'],
        ['یوآن چین', 'ریال عمان'],
        ['تومان (ایران)', 'انصراف و لغو']
    ]
    await update.message.reply_text(
        '۱. ابتدا مشخص کنید با چه ارزی پرداخت می‌کنید (مبدا):',
        reply_markup=ReplyKeyboardMarkup(currencies, one_time_keyboard=True, resize_keyboard=True)
    )
    return SOURCE_CURRENCY

async def select_target_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['source'] = update.message.text
    track_users_middleware(update.effective_user.id)
    currencies = [
        ['دلار آمریکا', 'تتر'],
        ['درهم امارات', 'لیر ترکیه'],
        ['پوند انگلیس', 'یورو'],
        ['یوآن چین', 'ریال عمان'],
        ['تومان (ایران)', 'انصراف و لغو']
    ]
    await update.message.reply_text(
        '۲. حالا مشخص کنید چه ارزی می‌خواهید دریافت کنید (مقصد):',
        reply_markup=ReplyKeyboardMarkup(currencies, one_time_keyboard=True, resize_keyboard=True)
    )
    return TARGET_AMOUNT

async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == 'انصراف و لغو':
        return await cancel(update, context)
    context.user_data['target'] = update.message.text
    track_users_middleware(update.effective_user.id)
    await update.message.reply_text(
        '۳. مقدار مورد نظر را به عدد وارد کنید (مثلا: 30000):',
        reply_markup=ReplyKeyboardRemove()
    )
    return CONTACT_INFO

async def get_contact_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['amount'] = update.message.text
    track_users_middleware(update.effective_user.id)
    await update.message.reply_text(
        '۴. نام و نام خانوادگی و شماره تماس گیرنده را ارسال کنید (مثلا علی رضایی 0912xxxxxxx):'
    )
    return ID_PHOTO

async def ask_for_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['contact'] = update.message.text
    track_users_middleware(update.effective_user.id)
    await update.message.reply_text(
        '۵. لطفاً عکس واضح از مدرک شناسایی (Emirates ID یا پاسپورت) را ارسال کنید. این مورد صرفاً جهت تطبیق هویت هنگام تحویل نقدی الزمی است.'
    )
    return WAIT_PHOTO

async def finalize_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_users_middleware(update.effective_user.id)
    order_num = get_next_order_number()
    photo_file = update.message.photo[-1]
    
    if ADMIN_CHAT_ID:
        try:
            header = format_customer_header(update.effective_user)
            summary = (
                f"🚨 سفارش جدید ثبت شد 🚨\n"
                f"🔢 شماره پیگیری: {order_num}\n\n"
                f"{header}\n"
                f"💵 ارز مبدا 💵: {context.user_data.get('source', '-')}\n"
                f"💷 ارز مقصد 💷: {context.user_data.get('target', '-')}\n"
                f"💰 مقدار 💰: {context.user_data.get('amount', '-')}\n"
                f"📞 مشخصات تماس 📞: {context.user_data.get('contact', '-')}"
            )
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=summary)
            await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=photo_file.file_id, caption="📸 تصویر مدارک مشتری")
        except Exception as e:
            logging.error(f"خطا در ارسال سفارش به ادمین: {e}")

    await update.message.reply_text(
        f'✅ سفارش شما با موفقیت ثبت شد و در دست بررسی است.\n🔢 شماره پیگیری: {order_num}',
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True)
    )
    context.user_data.clear()
    return ConversationHandler.END

async def remind_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_users_middleware(update.effective_user.id)
    await update.message.reply_text('لطفاً تصویر مدرک شناسایی را بفرستید! (یا برای لغو /cancel بزنید)')
    return WAIT_PHOTO

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_users_middleware(update.effective_user.id)
    await update.message.reply_text(
        'سفارش لغو شد.',
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True)
    )
    context.user_data.clear()
    return ConversationHandler.END

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    non_cancel_text = filters.TEXT & ~filters.COMMAND & ~filters.Regex("^(انصراف و لغو)$")

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^ثبت سفارش جدید$'), start_order)],
        states={
            SOURCE_CURRENCY: [MessageHandler(non_cancel_text, select_target_currency)],
            TARGET_AMOUNT: [MessageHandler(non_cancel_text, get_amount)],
            CONTACT_INFO: [MessageHandler(non_cancel_text, get_contact_info)],
            ID_PHOTO: [MessageHandler(non_cancel_text, ask_for_photo)],
            WAIT_PHOTO: [
                MessageHandler(filters.PHOTO, finalize_order),
                MessageHandler(filters.Document.IMAGE, finalize_order),
                MessageHandler(filters.TEXT & ~filters.Regex("^(انصراف و لغو)$"), remind_photo),
            ],
        },
        fallbacks=[MessageHandler(filters.Regex('^انصراف و لغو$'), cancel), CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.Regex('^نرخ لحظه‌ای$'), live_rates))
    application.add_handler(MessageHandler(filters.Regex('^پیگیری سفارش$'), track_order))
    application.add_handler(MessageHandler(filters.Regex('^ارتباط با ما$'), contact_us))
    application.add_handler(MessageHandler(filters.Regex('^درباره ما$'), about_us))

    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_to_admin))

    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
    )
