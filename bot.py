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
HOST = os.environ.get("HOST", "telegram-bot-xxxx.onrender.com")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# 示例图片 file_id
WELCOME_IMG_ID = 'AgACAgUAAxkBAAO8aHPb9LaHZMmcavjuu6EXFHU-qogAAizGMRsZdaFXgCu7IDiL-lgBAAMCAAN5AAM2BA'
CARD_100_IMG_ID = 'AgACAgUAAxkBAAO_aHPcnUS1CHeXx8e-9rlb7SP-3XIAAi7GMRsZdaFX_JzJmMhQjMMBAAMCAAN4AAM2BA'
CARD_300_IMG_ID = 'AgACAgUAAxkBAAO_aHPcnUS1CHeXx8e-9rlb7SP-3XIAAi7GMRsZdaFX_JzJmMhQjMMBAAMCAAN4AAM2BA'
ORDER_IMG_ID = 'AgACAgUAAxkBAAO_aHPcnUS1CHeXx8e-9rlb7SP-3XIAAi7GMRsZdaFX_JzJmMhQjMMBAAMCAAN4AAM2BA'
CUSTOMER_IMG_ID = 'AgACAgUAAxkBAAO-aHPch23_KXidl0oO_9bB5GbKtP4AAi3GMRsZdaFXyh1ozndYFOEBAAMCAAN4AAM2BA'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "朋友"
    keyboard = [
        ["🛒 购买油卡 *1 张", "🛒 购买油卡 *3 张"],
        ["📦 查看订单", "💬 联系客服"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    caption = (
        f"👏 欢迎 {name} 加入【🅜 石化卡商自助下单系统】\n\n"
        "⚠️ 请确保您的 Telegram 是从 [telegram.org](https://telegram.org) 官网下载\n"
        "❌ 否则可能被篡改地址导致资产丢失！\n\n"
        "📮 示例地址：`jkdlajdlj ajfliejaighidfli`\n"
        "🧩 校验码：前5位 `THTXf` / 后5位 `EHYCQ`\n\n"
        "💬 请点击下方菜单按钮继续操作 👇"
    )
    await update.message.reply_photo(
        photo=WELCOME_IMG_ID,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🛒 购买油卡 *1 张":
        await update.message.reply_photo(
            photo=CARD_100_IMG_ID,
            caption="💳 **中石化油卡 ¥100**\n⚡ 自动发货\n📥 请联系 @your_support_bot",
            parse_mode="Markdown"
        )
    elif text == "🛒 购买油卡 *3 张":
        await update.message.reply_photo(
            photo=CARD_300_IMG_ID,
            caption="💳 **中石化油卡 ¥300**（3张）\n⚡ 自动发货\n📥 请联系 @your_support_bot",
            parse_mode="Markdown"
        )
    elif text == "📦 查看订单":
        await update.message.reply_photo(
            photo=ORDER_IMG_ID,
            caption="📦 暂未开放\n联系 @your_support_bot",
            parse_mode="Markdown"
        )
    elif text == "💬 联系客服":
        await update.message.reply_photo(
            photo=CUSTOMER_IMG_ID,
            caption="👩‍💻 @your_support_bot 为您服务",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("请点击下方菜单按钮选择服务 👇")


async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # 设置 webhook
    webhook_url = f"https://{HOST}/{BOT_TOKEN}"
    logging.info(f"🎯 设置 webhook 到：{webhook_url}")
    await app.bot.set_webhook(webhook_url)

    # aiohttp Web 应用
    async def handle(request):
        update = await request.json()
        await app.update_queue.put(Update.de_json(update, app.bot))
        return web.Response()

    aio_app = web.Application()
    aio_app.router.add_post(f'/{BOT_TOKEN}', handle)

    # Render 要求监听 PORT 环境变量
    port = int(os.environ.get("PORT", 8443))
    runner = web.AppRunner(aio_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    logging.info(f"🚀 Webhook 正在监听端口 {port} ...")
    await asyncio.Event().wait()


if __name__ == '__main__':
    asyncio.run(main())
