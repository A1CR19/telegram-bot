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

# 环境变量
BOT_TOKEN = os.environ["BOT_TOKEN"]
HOST = os.environ.get("HOST", "telegram-bot-xxxx.onrender.com")
PORT = int(os.environ.get("PORT", 10000))

# 按钮菜单
KEYBOARD = [
    ["🛒 油卡 *1 张", "🛒 油卡 *3 张", "🛒 油卡 *5 张"],
    ["🛒 油卡 *10张", "🛒 油卡 *20张", "🛒 油卡 *30张"],
    ["🛒 电信卡 *1 张", "🛒 电信卡 *10 张", "🛒 电信卡 *30 张"],
    ["🛒 电信卡 *50 张", "🛒 电信卡 *100 张", "🛒 电信卡 *200 张"],
    ["🛒 京东E卡 *1 张", "🛒 京东E卡 *3 张", "🛒 京东E卡 *5 张"],
    ["🛒 京东E卡 *10张", "📦 提取卡密", "💬 在线客服"]
]

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "用户"
    logging.info(f"/start 触发，用户 {user.id} ({name})")

    welcome_text = (
        f"👏 欢迎 {name} 加入【🅜 石化卡商自助下单系统】\n\n"
        "使用自助提卡系统请确保您的 telegram 是从官网或 App Store 下载的。\n\n"
        "⚠️ 非官方版本可能会篡改地址，充值前请确认地址一致。\n\n"
        "官方地址示例：THTXfxxxxx...xxxxxEHYCQ"
    )

    keyboard_markup = ReplyKeyboardMarkup(KEYBOARD, resize_keyboard=True)

    try:
        await update.message.reply_text(
            welcome_text,
            reply_markup=keyboard_markup
        )
        logging.info("欢迎消息发送成功")
    except Exception as e:
        logging.error(f"发送欢迎消息失败: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        logging.info(f"收到消息：{text} 来自用户 {update.effective_user.id}")

        if text.startswith("🛒 油卡"):
            quantity = ''.join(filter(str.isdigit, text))
            price_per = 830
            total = int(quantity) * price_per
            usdt = round(total / 7.15, 2)

            reply = (
                f"🧾 商品：油卡\n"
                f"📦 数量：{quantity} 张\n"
                f"💰 单价：{price_per} 元\n"
                f"🧮 总价：{total} 元\n"
                f"💵 折合：{usdt} USDT\n\n"
                "💼 收款地址(USDT-TRC20)：\n"
                "THTXffejAMtqzYKW6Sxfmq8BXXz9yEHYCQ\n\n"
                "👆 点击复制钱包地址\n"
                "✅ 提币后点击『提取卡密』按钮\n"
                "📨 系统将自动发送您的卡密"
            )
            await update.message.reply_text(reply)

        elif text == "📦 提取卡密":
            await update.message.reply_text(
                "✅ 请发送交易截图进行审核\n"
                "🕐 审核时间 1-5 分钟\n"
                "⛔ 重复提交无效，请耐心等待"
            )

        elif text == "💬 在线客服":
            await update.message.reply_text("👩‍💻 请联系 @CCXR2025 客服协助")

        else:
            await update.message.reply_text("抱歉，无法识别您的消息，请使用菜单按钮进行操作。")

    except Exception as e:
        logging.error(f"处理用户消息时出错: {e}")

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
