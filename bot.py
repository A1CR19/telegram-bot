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

# ==== 环境变量配置 ====
BOT_TOKEN = os.getenv("BOT_TOKEN")
HOST = "telegram-bot-28w5.onrender.com"  # 你的 Render 子域名
PORT = int(os.getenv("PORT", "10000"))

if not BOT_TOKEN or not HOST:
    raise RuntimeError("请确保环境变量 BOT_TOKEN 和 HOST 已设置")

# ==== 日志配置 ====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ==== 图片 file_id ====
WELCOME_IMG_ID = 'AgACAgUAAxkBAAO8aHPb9LaHZMmcavjuu6EXFHU-qogAAizGMRsZdaFXgCu7IDiL-lgBAAMCAAN5AAM2BA'
CARD_IMG_ID = 'AgACAgUAAxkBAAO_aHPcnUS1CHeXx8e-9rlb7SP-3XIAAi7GMRsZdaFX_JzJmMhQjMMBAAMCAAN4AAM2BA'
CUSTOMER_IMG_ID = 'AgACAgUAAxkBAAO-aHPch23_KXidl0oO_9bB5GbKtP4AAi3GMRsZdaFXyh1ozndYFOEBAAMCAAN4AAM2BA'

# ==== 产品价格 ====
PRODUCTS = {
    "油卡": 830,
    "电信卡": 88,
    "京东E卡": 815
}
USDT_RATE = 7.15


# ==== /start 命令处理函数 ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        name = update.effective_user.first_name or "朋友"
        keyboard = [
            ["🛒 油卡 *1 张", "🛒 油卡 *3 张", "🛒 油卡 *5 张"],
            ["🛒 油卡 *10张", "🛒 油卡 *20张", "🛒 油卡 *30张"],
            ["🛒 电信卡 *1 张", "🛒 电信卡 *10 张", "🛒 电信卡 *30 张"],
            ["🛒 电信卡 *50 张", "🛒 电信卡 *100 张", "🛒 电信卡 *200 张"],
            ["🛒 京东E卡 *1 张", "🛒 京东E卡 *3 张", "🛒 京东E卡 *5 张"],
            ["🛒 京东E卡 *10张", "📦 提取卡密", "💬 在线客服"]
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
        await update.message.reply_photo(photo=WELCOME_IMG_ID, caption=caption, parse_mode="Markdown", reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"/start 出错: {e}", exc_info=True)
        await update.message.reply_text("🤖 系统异常，请稍后再试")


# ==== 普通消息处理函数 ====
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
                "- 提币后请点击“提取卡密”按钮获取卡密"
            )
            await update.message.reply_photo(photo=CARD_IMG_ID, caption=caption, parse_mode="Markdown")
        elif text == "💬 在线客服":
            await update.message.reply_photo(photo=CUSTOMER_IMG_ID, caption="👩‍💻 联系客服 @CCXR2025")
        elif text == "📦 提取卡密":
            await update.message.reply_photo(photo=CUSTOMER_IMG_ID, caption="请发送交易截图，我们会在1~5分钟内回复您")
        else:
            await update.message.reply_text("📌 请点击下方菜单按钮选择服务 👇")

    except Exception as e:
        logger.error(f"消息处理失败: {e}", exc_info=True)
        await update.message.reply_text("🤖 操作失败，请联系客服")


# ==== 错误处理函数 ====
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"未捕获异常: {context.error}", exc_info=True)
    if update and update.message:
        await update.message.reply_text("⚠️ 系统故障，请稍后再试")


# ==== 主函数启动 webhook ====
async def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    webhook_url = f"https://{HOST}/{BOT_TOKEN}"
    await application.bot.set_webhook(webhook_url)
    logger.info(f"Webhook 设置成功：{webhook_url}")

    # aiohttp 服务处理 Telegram 的 webhook 请求
    async def handle(request):
        try:
            update_data = await request.json()
            await application.update_queue.put(Update.de_json(update_data, application.bot))
            return web.Response(text="ok")
        except Exception as e:
            logger.error(f"Webhook 处理请求异常: {e}", exc_info=True)
            return web.Response(status=500, text="error")

    aio_app = web.Application()
    aio_app.router.add_post(f"/{BOT_TOKEN}", handle)
    aio_app.router.add_get("/health", lambda request: web.Response(text="Bot 正常运行"))

    runner = web.AppRunner(aio_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    logger.info(f"Bot 已上线，监听端口: {PORT}")

    # 启动 PTB 应用（但不再使用 .start_webhook()）
    await application.initialize()
    await application.start()

    # 保持运行
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
