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

# Telegram Bot Token 和 Render Webhook 设置
BOT_TOKEN = os.environ["BOT_TOKEN"]
HOST = os.environ.get("HOST", "your-render-url.onrender.com")
PORT = int(os.environ.get("PORT", 10000))

# 日志设置
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ✅ 最新 file_id 设置
WELCOME_IMG_ID = 'AgACAgUAAxkBAAIBUGh0y55xlUF2ZOtfQWCqfrYLkPxAAAKkwzEb2A-oV9o2cdjw8AABjQEAAwIAA3kAAzYE'
CARD_IMG_ID    = 'AgACAgUAAxkBAAIBUWh0y6tuD5xFARfsvqmpSvvT2XWaAAKlwzEb2A-oV8ekyaeITog4AQADAgADeAADNgQ'
ORDER_IMG_ID   = 'AgACAgUAAxkBAAIBUmh0y7sWksHtM2J14K1sxyVvQ3LxAALJxzEbGXWhV98_2_ux2OlTAQADAgADeAADNgQ'
CUSTOMER_IMG_ID= 'AgACAgUAAxkBAAIBU2h0y81tRjBAc1xjygz2ase5ZZr4AAKmwzEb2A-oV9fiw7wCJ6moAQADAgADeAADNgQ'

# 商品信息
PRODUCTS = {
    "油卡": 830,
    "电信卡": 88,
    "京东E卡": 815
}
USDT_RATE = 7.15


# 开始指令响应
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("机器人在线，欢迎使用！")
    logging.info("发送了测试文本回复")

# 用户点击按钮的处理函数
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    logging.info(f"收到消息文本: {text}")

    if text.startswith("🛒"):
        try:
            parts = text.replace("🛒", "").replace("张", "").split("*")
            card_type = parts[0].strip()
            quantity = int(parts[1].strip())
            price = PRODUCTS.get(card_type)

            if price:
                total = price * quantity
                usdt = round(total / USDT_RATE)
                caption = (
                    f"单价：{price}元/张\n"
                    f"数量：{quantity}张\n"
                    f"总价：{total}元\n"
                    f"折合：{usdt} USDT\n"
                    f"优惠：无\n"
                    "💼 收款地址(USDT-TRC20)：\n\n"
                    "THTXffejAMtqzYKW6Sxfmq8BXXz9yEHYCQ\n\n"
                    "👆 点击复制钱包, 地址尾号 EHYCQ 👆\n\n"
                    "提示：\n"
                    "- 提币后请点击（提取卡密）按钮，Bot 会发送专属提卡密令！\n"
                    "- 激活成功后，Bot 会立刻发送您的卡号卡密。"
                )
                await update.message.reply_photo(photo=CARD_IMG_ID, caption=caption)
            else:
                await update.message.reply_text("暂不支持该商品类型，请联系客服 @CCXR2025")
        except Exception as e:
            logging.error(f"商品消息处理失败：{e}")
            await update.message.reply_text("格式有误，请重新选择商品")

    elif text == "💬 在线客服":
        await update.message.reply_photo(
            photo=CUSTOMER_IMG_ID,
            caption="👩‍💻 @CCXR2025 为您服务"
        )

    elif text == "📦 提取卡密":
        await update.message.reply_photo(
            photo=ORDER_IMG_ID,
            caption=(
                "✅ 请向我发送您的交易截图进行审核\n"
                "🌐 预计时长 1~5 分钟，重复提交无效\n"
                "🗣 审核通过后，Bot 会通知您\n"
                "⏳ 请耐心等待……"
            )
        )

    else:
        await update.message.reply_text("请点击下方菜单按钮选择服务 👇")


# 主函数：设置 webhook 与 aiohttp 服务器
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    webhook_url = f"https://{HOST}/{BOT_TOKEN}"
    logging.info(f"设置 webhook 到：{webhook_url}")
    await app.bot.set_webhook(webhook_url)

    async def handle(request):
        update_data = await request.json()
        logging.info(f"收到请求数据: {update_data}")
        await app.update_queue.put(Update.de_json(update_data, app.bot))
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
