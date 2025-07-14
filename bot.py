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

# 环境变量读取
BOT_TOKEN = os.environ["BOT_TOKEN"]
HOST = os.environ.get("HOST", "your-render-url.onrender.com")
PORT = int(os.environ.get("PORT", 10000))

# 日志配置
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# 图片 file_id
WELCOME_IMG_ID = 'AgACAgUAAxkBAAO8aHPb9LaHZMmcavjuu6EXFHU-qogAAizGMRsZdaFXgCu7IDiL-lgBAAMCAAN5AAM2BA'
CARD_IMG_ID = 'AgACAgUAAxkBAAO_aHPcnUS1CHeXx8e-9rlb7SP-3XIAAi7GMRsZdaFX_JzJmMhQjMMBAAMCAAN4AAM2BA'
CUSTOMER_IMG_ID = 'AgACAgUAAxkBAAO-aHPch23_KXidl0oO_9bB5GbKtP4AAi3GMRsZdaFXyh1ozndYFOEBAAMCAAN4AAM2BA'

PRODUCTS = {
    "油卡": 830,
    "电信卡": 88,
    "京东E卡": 815
}
USDT_RATE = 7.15  # 汇率

# /start 命令处理函数
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        "`THTXffejAMtqzYKW6Sxfmq8BXXz9yEHYCQ`\n\n"
        "⚠️ 请核对地址：前5位 `THTXf`，后5位 `EHYCQ`\n\n"
        "如不一致则您使用了盗版客户端，请停止充值！"
    )
    await update.message.reply_photo(
        photo=WELCOME_IMG_ID,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# 文本消息处理函数
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
                usdt = round(total / USDT_RATE, 2)
                caption = (
                    f"🧾 商品：{card_type}\n"
                    f"📦 数量：{quantity} 张\n"
                    f"💰 单价：{price} 元\n"
                    f"🧮 总价：{total} 元\n"
                    f"💵 折合：{usdt} USDT\n\n"
                    "💼 收款地址(USDT-TRC20)：\n"
                    "`THTXffejAMtqzYKW6Sxfmq8BXXz9yEHYCQ`\n\n"
                    "👆 点击复制钱包地址，尾号：`EHYCQ`\n\n"
                    "✅ 提币后点击『提取卡密』按钮\n"
                    "📨 系统将自动发送您的卡密"
                )
                await update.message.reply_photo(
                    photo=CARD_IMG_ID,
                    caption=caption,
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text("暂不支持该卡种，请联系客服 @CCXR2025")
        except Exception as e:
            logging.error(f"商品处理错误：{e}")
            await update.message.reply_text("格式错误，请重新选择菜单选项")

    elif text == "💬 在线客服":
        await update.message.reply_photo(
            photo=CUSTOMER_IMG_ID,
            caption="👩‍💻 请联系 @CCXR2025 客服协助"
        )

    elif text == "📦 提取卡密":
        await update.message.reply_photo(
            photo=CUSTOMER_IMG_ID,
            caption=(
                "✅ 请发送交易截图进行审核\n"
                "🕐 审核时间 1-5 分钟\n"
                "⛔ 重复提交无效，请耐心等待"
            )
        )

    else:
        await update.message.reply_text("请点击下方菜单选择卡种 👇")

# 主函数
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler(["start", "开始"], start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # 启动 bot 的处理器，初始化队列
    await app.initialize()
    await app.start()

    # 设置 Webhook 地址
    webhook_url = f"https://{HOST}/{BOT_TOKEN}"
    logging.info(f"设置 webhook 到：{webhook_url}")
    await app.bot.set_webhook(webhook_url)

    # aiohttp 创建 webhook 接口
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

    logging.info(f"✅ Webhook 正在监听端口 {PORT}")

    # 阻止程序退出（阻塞）
    await asyncio.Event().wait()


