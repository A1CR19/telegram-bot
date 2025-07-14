import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = os.environ.get("BOT_TOKEN", "你的TOKEN")
PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL = f"https://你的子域名.onrender.com/{TOKEN}"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("🛒 油卡 *1 张", callback_data="buy_1")],
        [InlineKeyboardButton("📦 油卡 *3 张", callback_data="buy_3")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("欢迎使用自助下单系统，请选择购买数量：", reply_markup=reply_markup)

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "buy_1":
        await query.edit_message_text("您选择了购买 1 张油卡，请稍等...")
    elif query.data == "buy_3":
        await query.edit_message_text("您选择了购买 3 张油卡，马上为您处理...")

def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=WEBHOOK_URL,
    )

if __name__ == '__main__':
    main()
