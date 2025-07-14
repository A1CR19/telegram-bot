import os
import logging
import asyncio

from telegram import Update
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
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("机器人已启动，欢迎使用！")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    logging.info(f"收到消息：{text}，来自用户：{update.effective_user.id}")
    await update.message.reply_text("收到你的消息啦！")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    webhook_url = f"https://{HOST}/{BOT_TOKEN}"
    logging.info(f"设置 webhook 到：{webhook_url}")
    await app.bot.set_webhook(webhook_url)

    async def handle(request):
        update_data = await request.json()
        logging.info(f"收到请求数据: {update_data}")
        update = Update.de_json(update_data, app.bot)
        await app.update_queue.put(update)
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
