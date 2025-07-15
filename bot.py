import os
import logging
import asyncio
import traceback
from aiohttp import web  
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
WELCOME_IMG_ID = "AgACAgUAAxkBAANPaHUn1r5m5oB_JIbQigdPXJhwmxYAAiTHMRsZdalXJuST3sL6uMcBAAMCAAN5AAM2BA"
CARD_IMG_ID = "AgACAgUAAxkBAANRaHUoObVyzozfIUFl2TtEhb-fVK0AAiXHMRsZdalXvBdO3ULb5MoBAAMCAAN4AAM2BA"
CUSTOMER_IMG_ID = "AgACAgUAAxkBAANSaHUoT5PQQ0us-ioKGBpqUtGj7A8AAibHMRsZdalXZEXuLH22sDcBAAMCAAN4AAM2BA"
TQKM_IMG_ID = "AgACAgUAAxkBAANTaHUoXVb5SzcW2aNNucWxXnXnsAkAAlzEMRtYPalXFQ8O3LdPINYBAAMCAAN4AAM2BA"

PRODUCTS = {
    "油卡": 830,
    "电信卡": 88,
    "京东E卡": 815,
}
USDT_RATE = 7.15

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        name = update.effective_user.first_name or "朋友"
        keyboard = [
            ["🛒 油卡 *1 张", "🛒 油卡 *3 张", "🛒 油卡 *5 张"],
            ["🛒 油卡 *10张", "🛒 油卡 *20张", "🛒 油卡 *30张"],
            ["🛒 电信卡 *1 张", "🛒 电信卡 *10 张", "🛒 电信卡 *30 张"],
            ["🛒 电信卡 *50 张", "🛒 电信卡 *100 张", "🛒 电信卡 *200 张"],
            ["🛒 京东E卡 *1 张", "🛒 京东E卡 *3 张", "🛒 京东E卡 *5 张"],
            ["🛒 京东E卡 *10张", "📦 提取卡密", "💬 在线客服"],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        caption = (
            f"👏 欢迎 {name} 加入【🅜 石化卡商自助下单系统】\n\n"
            "使用自助提卡系统请确保您的telegram是从AppStore或者官网下载!\n【 https://telegram.org/ 】\n"
            "网络上下载的中文版telegram是有病毒的,会自动替换您收到的地址\n\n"
            "由于系统是自动生成地址,无法上传地址的二维码图片供您核对\n\n"
            "THTXffejAMtqzYKW6Sxfmq8BXXz9yEHYCQ\n\n"
            "⚠️上述地址前5位为THTXf后5位为EHYCQ\n"
            "如不一致则意味着您使用了盗版客户端，请停止充值\n\n"
            "💬 如不确定,切勿提币,请联系在线客服核验!"
        )
        await update.message.reply_photo(
            photo=WELCOME_IMG_ID, caption=caption, parse_mode="Markdown", reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"/start 出错: {e}\n{traceback.format_exc()}")
        await update.message.reply_text("🤖 系统异常，请稍后再试")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.strip()
        logger.info(f"收到用户消息: {text}")

        if text.startswith("🛒"):
            parts = text.replace("🛒", "").replace("张", "").split("*")
            if len(parts) != 2:
                await update.message.reply_text("格式错误，请使用菜单按钮下单")
                return
            card_type = parts[0].strip()
            quantity = int(parts[1].strip())
            price = PRODUCTS.get(card_type)
            if price is None:
                await update.message.reply_text("商品不存在，请联系客服")
                return
            total = price * quantity
            usdt = round(total / USDT_RATE)
            caption = (
                f"单价：{price}元/张\n数量：{quantity}张\n总价：{total}元\n"
                f"折合：{usdt} USDT\n优惠：无\n"
                "💼 收款地址(USDT-TRC20)：\n\n"
                "THTXffejAMtqzYKW6Sxfmq8BXXz9yEHYCQ\n\n"
                "👆 点击复制钱包, 地址尾号 EHYCQ 👆\n\n"
                "- 提示："
                "- 对上述地址👆交易所或钱包提币会有1-3分钟确认期，请等待确认提币成功后点击（提取卡密） 后 Bot 会为您发送个人提卡密令，请妥善保管好，请勿与他人分享！\n"
                "- 请耐心等待，密令激活成功后 Bot 会通立即发送您的对应卡号卡密！"
            )
            await update.message.reply_photo(photo=CARD_IMG_ID, caption=caption, parse_mode="Markdown")
        elif text == "💬 在线客服":
            caption = (
                "👩‍💻 中油国际客服 @CCXR2025\n\n"
                "🌐 🌐 🌐 🌐 🌐 🌐 🌐\n"
                "🗣 在线时间上午10点~晚上12点\n"
            )
            await update.message.reply_photo(photo=CUSTOMER_IMG_ID, caption=caption)
        elif text == "📦 提取卡密":
            caption = (
                "✅ 请向我发送您的交易截图进行审核\n"
                "🌐 预计时长 1~5 分钟，重复提交无效\n"
                "🗣 审核通过后，Bot 会通知您\n"
                "⏳ 请耐心等待...…"
            )
            await update.message.reply_photo(photo=TQKM_IMG_ID, caption=caption)
        else:
            await update.message.reply_text("📌 请点击下方菜单按钮选择服务 👇")
    except Exception as e:
        logger.error(f"消息处理失败: {e}\n{traceback.format_exc()}")
        await update.message.reply_text("🤖 操作失败，请联系客服")

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
