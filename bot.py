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
HOST = os.environ.get("HOST", "telegram-bot-28w5.onrender.com")
PORT = int(os.environ.get("PORT", 10000))

# 图片 file_id（替换为你自己的）
WELCOME_IMG_ID = 'AgACAgUAAxkBAAO8aHPb9LaHZMmcavjuu6EXFHU-qogAAizGMRsZdaFXgCu7IDiL-lgBAAMCAAN5AAM2BA'
CARD_IMG_ID = 'AgACAgUAAxkBAAO_aHPcnUS1CHeXx8e-9rlb7SP-3XIAAi7GMRsZdaFX_JzJmMhQjMMBAAMCAAN4AAM2BA'
CUSTOMER_IMG_ID = 'AgACAgUAAxkBAAO-aHPch23_KXidl0oO_9bB5GbKtP4AAi3GMRsZdaFXyh1ozndYFOEBAAMCAAN4AAM2BA'

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

    caption = (
        f"👏 欢迎 {name} 加入【🅜 石化卡商自助下单系统】\n\n"
        "使用自助提卡系统请确保您的telegram是从AppStore或者官网下载!\n【 https://telegram.org/ 】\n"
        "网络上下载的中文版telegram是有病毒的,会自动替换您收到的地址\n\n"
        "由于系统是自动生成地址,无法上传地址的二维码图片供您核对\n\n"
        "`THTXffejAMtqzYKW6Sxfmq8BXXz9yEHYCQ`\n\n"
        "⚠️ 请核对地址：前5位 `THTXf`，后5位 `EHYCQ`\n\n"
        "如不一致则您使用了盗版客户端，请停止充值！"
    )

    keyboard_markup = ReplyKeyboardMarkup(KEYBOARD, resize_keyboard=True)

    try:
        await update.message.reply_photo(
            photo=WELCOME_IMG_ID,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=keyboard_markup,
        )
        logging.info("欢迎消息发送成功")
    except Exception as e:
        logging.error(f"发送欢迎消息失败: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    logging.info(f"收到消息：{text} 来自用户 {update.effective_user.id}")

    # 简单解析购买请求示例
    if text.startswith("🛒 油卡"):
        quantity = ''.join(filter(str.isdigit, text))
        price_per = 830
        total = int(quantity) * price_per
        usdt = round(total / 7.15, 2)

        caption = (
            f"🧾 商品：油卡\n"
            f"📦 数量：{quantity} 张\n"
            f"💰 单价：{price_per} 元\n"
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
    elif text == "📦 提取卡密":
        await update.message.reply_photo(
            photo=CUSTOMER_IMG_ID,
            caption=(
                "✅ 请发送交易截图进行审核\n"
                "🕐 审核时间 1-5 分钟\n"
                "⛔ 重复提交无效，请耐心等待"
            )
        )
    elif text == "💬 在线客服":
        await update.message.reply_photo(
            photo=CUSTOMER_IMG_ID,
            caption="👩‍💻 请联系 @CCXR2025 客服协助"
        )
    else:
        # 默认回复
        await update.message.reply_text("抱歉，无法识别您的消息，请使用菜单按钮进行操作。")

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
