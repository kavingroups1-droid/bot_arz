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

# تنظیمات لاگین
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "YOUR_NEW_TOKEN_HERE"
SUPPORT_CONTACT = "+971544048575"
ORDER_FILE = "order_number.txt"

# تابع مدیریت شماره سفارش
def get_next_order_number():
    if not os.path.exists(ORDER_FILE):
        current_number = 1149
    else:
        try:
            with open(ORDER_FILE, "r") as f:
                current_number = int(f.read().strip())
        except Exception:
            current_number = 1149
            
    next_number = current_number + 1
    with open(ORDER_FILE, "w") as f:
        f.write(str(next_number))
    return next_number

# مراحل گفتگو برای ثبت سفارش
SOURCE_CURRENCY, TARGET_AMOUNT, CONTACT_INFO, ID_PHOTO = range(4)

# منوی اصلی
MAIN_MENU_KEYBOARD = [
    ['ثبت سفارش جدید'],
    ['نرخ لحظه‌ای', 'پیگیری سفارش'],
    ['ارتباط با ما', 'درباره ما']
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'به صرافی خوش آمدید. لطفاً از منوی زیر گزینه مورد نظر خود را انتخاب کنید:',
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True)
    )

async def live_rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '📈 استعلام نرخ لحظه‌ای\n\n'
        'با توجه به نوسانات دقیقه‌ای بازار، جهت دریافت دقیق‌ترین نرخ‌ها لطفاً به شماره واتس‌اپ ما پیام دهید:\n'
        f'{SUPPORT_CONTACT}'
    )

async def track_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '🔍 پیگیری سفارش\n\n'
        'برای پیگیری وضعیت سفارش خود، لطفاً شماره پیگیری یا نام خود را به پشتیبانی تلگرام یا واتس‌اپ ما ارسال نمایید:\n'
        f'{SUPPORT_CONTACT}'
    )

async def contact_us(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '📞 ارتباط با ما و راهنما\n\n'
        'پشتیبانی ۲۴ ساعته و واتس‌اپ:\n'
        f'{SUPPORT_CONTACT}\n\n'
        'پاسخگوی به سوالات شما هستیم.'
    )

async def about_us(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '🏢 درباره ما\n\n'
        'صرافی ما با سال‌ها تجربه درخشان در زمینه حواله‌جات ارزی، امن‌ترین و سریع‌ترین خدمات را با بهترین نرخ به شما ارائه می‌دهد.'
    )

async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    await update.message.reply_text(
        '۳. مقدار مورد نظر را به عدد وارد کنید (مثلا: 30000):',
        reply_markup=ReplyKeyboardRemove()
    )
    return CONTACT_INFO

async def get_contact_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['amount'] = update.message.text
    await update.message.reply_text(
        '۴. نام و نام خانوادگی و شماره تماس گیرنده را ارسال کنید (مثلا علی رضایی 0912xxxxxxx):'
    )
    return ID_PHOTO

async def finalize_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['contact'] = update.message.text
    await update.message.reply_text(
        '۵. لطفاً عکس واضح از مدرک شناسایی (Emirates ID یا پاسپورت) را ارسال کنید. این مورد صرفاً جهت تطبیق هویت هنگام تحویل نقدی الزمی است.'
    )
    return ConversationHandler.END

async def order_complete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    order_num = get_next_order_number()
    await update.message.reply_text(
        f'✅ سفارش شما با موفقیت ثبت شد و در دست بررسی است.\n🔢 شماره پیگیری: {order_num}',
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True)
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'سفارش لغو شد.',
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True)
    )
    return ConversationHandler.END

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^ثبت سفارش جدید$'), start_order)],
        states={
            SOURCE_CURRENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_target_currency)],
            TARGET_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount)],
            CONTACT_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact_info)],
            ID_PHOTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, finalize_order)],
        },
        fallbacks=[MessageHandler(filters.Regex('^انصراف و لغو$'), cancel), CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.Regex('^نرخ لحظه‌ای$'), live_rates))
    application.add_handler(MessageHandler(filters.Regex('^پیگیری سفارش$'), track_order))
    application.add_handler(MessageHandler(filters.Regex('^ارتباط با ما$'), contact_us))
    application.add_handler(MessageHandler(filters.Regex('^درباره ما$'), about_us))
    
    # هندلر نهایی برای پیام بعد از عکس
    application.add_handler(MessageHandler(filters.PHOTO, order_complete))

    application.run_polling()
