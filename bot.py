import os
import logging
import asyncio

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from aiohttp import web

BOT_TOKEN = os.environ["BOT_TOKEN"]
HOST = os.environ.get("HOST", "telegram-bot-xxxx.onrender.com")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"处理 /start 来自 {update.effective_user.id}")
    await update.message.reply_text("欢迎使用测试机器人！发送消息试试吧。")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"收到消息: {update.message.text} 来自 {update.effective_user.id}")
    await update.message.reply_text(f"你说了：{update.message.text}")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    webhook_url = f"https://{HOST}/{BOT_TOKEN}"
    logging.info(f"设置 webhook 到：{webhook_url}")
    await app.bot.set_webhook(webhook_url)

    async def handle(request):
        update = await request.json()
        logging.info(f"收到请求数据: {update}")
        await app.update_queue.put(Update.de_json(update, app.bot))
        return web.Response()

    aio_app = web.Application()
    aio_app.router.add_post(f'/{BOT_TOKEN}', handle)

    port = int(os.environ.get("PORT", 8443))
    runner = web.AppRunner(aio_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    logging.info(f"Webhook 正在监听端口 {port} ...")
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
