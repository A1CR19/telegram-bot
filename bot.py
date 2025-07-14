import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ["BOT_TOKEN"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"/start 被调用，用户：{update.effective_user.id}")
    try:
        await update.message.reply_text("欢迎使用测试机器人！")
    except Exception as e:
        logging.error(f"回复失败: {e}")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    # 设置 webhook
    webhook_url = f"https://telegram-bot-28w5.onrender.com/{BOT_TOKEN}"
    logging.info(f"设置 webhook 到：{webhook_url}")
    await app.bot.set_webhook(webhook_url)

    # aiohttp 监听请求
    from aiohttp import web

    async def handle(request):
        data = await request.json()
        logging.info(f"收到请求数据: {data}")
        await app.update_queue.put(Update.de_json(data, app.bot))
        return web.Response()

    aio_app = web.Application()
    aio_app.router.add_post(f'/{BOT_TOKEN}', handle)

    port = int(os.environ.get("PORT", 8443))
    runner = web.AppRunner(aio_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    logging.info(f"Webhook 正在监听端口 {port}")
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
