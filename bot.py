import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))

# ✅ 修改路径：固定 webhook endpoint
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://telegram-bot-28w5.onrender.com{WEBHOOK_PATH}"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛒 油卡 *1 张", callback_data="buy_1")],
        [InlineKeyboardButton("📦 油卡 *3 张", callback_data="buy_3")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("欢迎使用自助下单系统，请选择购买数量：", reply_markup=reply_markup)

async def button_handler(update, context: ContextTypes.DEFAULT_TYPE):
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
        url_path=WEBHOOK_PATH.lstrip("/"),  # ✅ 注意不带 "/"
        webhook_url=WEBHOOK_URL,
    )

if __name__ == '__main__':
    main()
