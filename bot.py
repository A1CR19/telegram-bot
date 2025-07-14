import os
import logging
import asyncio

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from aiohttp import web

BOT_TOKEN = os.environ["BOT_TOKEN"]
HOST = os.environ.get("HOST", "your-render-url.onrender.com")
PORT = int(os.environ.get("PORT", 10000))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

PRODUCTS = {
    "油卡": 830,
    "电信卡": 88,
    "京东E卡": 815
}
USDT_RATE = 7.15

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logging.info(f"/start 被触发，用户：{user.id} @{user.username}")

    try:
        await update.message.reply_text("机器人在线，欢迎使用！")
        logging.info("发送欢迎文本消息成功")
        await update.message.reply_text(f"你的用户名是：{user.username}，ID是：{user.id}")
    except Exception as e:
        logging.error(f"发送欢迎消息失败：{e}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"收到消息：{update.message.text} 来自用户 {update.effective_user.id}")
    await update.message.reply_text("收到你的消息啦！")  # 简单回声测试

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    webhook_url = f"https://{HOST}/{BOT_TOKEN}"
    logging.info(f"设置 webhook 到：{webhook_url}")
    await app.bot.set_webhook(webhook_url)

    async def handle(request):
        try:
            update_data = await request.json()
            logging.info(f"收到请求数据: {update_data}")
            update = Update.de_json(update_data, app.bot)
            await app.update_queue.put(update)
            logging.info("更新放入队列成功")
        except Exception as e:
            logging.error(f"Webhook 处理失败: {e}")
            return web.Response(status=500, text="Internal Server Error")
        return web.Response()

    aio_app = web.Application()
    aio_app.router.add_post(f'/{BOT_TOKEN}', handle)

    runner = web.AppRunner(aio_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    logging.info(f"Webhook 正在监听端口 {PORT}")
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
