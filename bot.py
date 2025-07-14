import os
import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))
HOST = os.environ.get("HOST", "0.0.0.0")
URL = os.environ.get("RENDER_EXTERNAL_URL") or f"https://your-subdomain.onrender.com"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 按钮文字
button_texts = [
    ["购买卡类商品", "联系客服"]
]

keyboard = ReplyKeyboardMarkup(
    [[KeyboardButton(text) for text in row] for row in button_texts], resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "欢迎使用自助系统，请选择以下操作："
    await update.message.reply_photo(
        photo="<你的欢迎图片 file_id>",
        caption=welcome_text,
        reply_markup=keyboard
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    if user_text == "购买卡类商品":
        await update.message.reply_photo(
            photo="<商品图片 file_id>",
            caption="🔥 特价商品：Netflix 会员卡，仅需 5 USDT",
        )
    elif user_text == "联系客服":
        await update.message.reply_text("请联系 @你的客服账号，我们将尽快回复您。")
    else:
        await update.message.reply_text("🤖 系统异常，请稍后再试")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).webhook(
        listen=HOST,
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"{URL}/{BOT_TOKEN}"
    ).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("Bot 已上线，监听端口: %s", PORT)
    await app.run_webhook()

if __name__ == '__main__':
    import asyncio
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")
