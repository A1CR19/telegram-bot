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
logger = logging.getLogger(__name__)  # ✅ 加上这行

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


# ==== 错误处理函数 ====
async def error_handler(update, context):
    logger.error(f"未捕获异常: {context.error}\n{traceback.format_exc()}")
    if update and update.message:
        await update.message.reply_text("⚠️ 系统故障，请稍后再试")

# 替换 main 函数部分

async def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    webhook_url = f"https://{HOST}/{BOT_TOKEN}"
    await application.bot.set_webhook(webhook_url)
    logger.info(f"Webhook 设置成功：{webhook_url}")

    # aiohttp 接收 Telegram 推送
    async def handle(request):
        try:
            data = await request.json()
            update = Update.de_json(data, application.bot)
            await application.update_queue.put(update)
            return web.Response(text="ok")
        except Exception as e:
            logger.error(f"Webhook 请求处理失败: {e}\n{traceback.format_exc()}")
            return web.Response(status=500, text="error")

    # aiohttp 服务设置
    aio_app = web.Application()
    aio_app.router.add_post(f"/{BOT_TOKEN}", handle)
    aio_app.router.add_get("/health", lambda request: web.Response(text="Bot 正常运行"))

    runner = web.AppRunner(aio_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    logger.info(f"✅ Bot 启动完成，监听 {PORT} 端口，等待 Telegram 请求")

    await application.initialize()
    await application.start()
    await asyncio.Event().wait()  # 永远不退出


if __name__ == '__main__':
    import asyncio
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")
