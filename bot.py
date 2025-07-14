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
CARD_IMG_ID  = 'AgACAgUAAxkBAAO_aHPcnUS1CHeXx8e-9rlb7SP-3XIAAi7GMRsZdaFX_JzJmMhQjMMBAAMCAAN4AAM2BA'
CUSTOMER_IMG_ID = 'AgACAgUAAxkBAAO-aHPch23_KXidl0oO_9bB5GbKtP4AAi3GMRsZdaFXyh1ozndYFOEBAAMCAAN4AAM2BA'

# 商品单价表（单位：元/张）
PRODUCTS = {
    "油卡": 830,
    "电信卡": 88,
    "京东E卡": 815
}

# 汇率（假设 1 USDT = 7.15 元，实际根据情况调整）
USDT_RATE = 7.15

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "朋友"
    keyboard = [
        ["🛒 油卡 *1 张", "🛒 油卡 *3 张", "🛒 油卡 *5 张"],
        ["🛒 油卡 *10张", "🛒 油卡 *20张", "🛒 油卡 *30张"],
        ["🛒 电信卡 *1 张", "🛒 电信卡 *10 张", "🛒 电信卡 *30 张"],
        ["🛒 电信卡 *50 张", "🛒 电信卡 *100 张", "🛒 电信卡 *200 张"],
        ["🛒 京东E卡 *1 张", "🛒 京东E卡 *3 张", "🛒 京东E卡 *5 张"],
        ["🛒 京东E卡 *10张","📦 提取卡密", "💬 在线客服"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    caption = (
        f"👏 欢迎 {name} 加入【🅜 石化卡商自助下单系统】\n\n"
        "使用自助提卡系统请确保您的telegram是从AppStore或者官网下载!\n【 https://telegram.org/ 】\n"
        "网络上下载的中文版telegram是有病毒的,会自动替换您收到的地址\n\n"
        "由于系统是自动生成地址,无法上传地址的二维码图片供您核对\n\n"
        "THTXffejAMtqzYKW6Sxfmq8BXXz9yEHYCQ\n\n"
        "【THTXffej……z9yEHYCQ】请核对前后八位数字和字母\n\n"
        "⚠️上述地址前5位为THTXf后5位为 EHYCQ\n如不一致则意味着您使用了盗版客户端，请停止充值\n\n"
        "同时谨防人为上传带图片地址的系统,本系统从未对外授权\n\n"
        "💬 如不确定,切勿提币,请联系在线客服核验! "
    )
    await update.message.reply_photo(
        photo=WELCOME_IMG_ID,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


# 处理消息
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
                await update.message.reply_photo(photo=CARD_IMG_ID, caption=caption, parse_mode="Markdown")
            else:
                await update.message.reply_text("暂不支持类型，请联系客服@CCXR2025")
        except Exception as e:
            logging.error(f"处理商品信息失败：{e}")
            await update.message.reply_text("格式有误，请重新选择商品")

    elif text == "💬 在线客服":
        await update.message.reply_photo(photo=CUSTOMER_IMG_ID, caption="👩‍💻 @CCXR2025 为您服务")
    elif text == "📦 提取卡密":
        await update.message.reply_photo(
            photo=CUSTOMER_IMG_ID,
            caption=(
                "✅ 请向我发送您的交易截图进行审核\n"
                "🌐 预计时长 1~5 分钟，重复提交无效\n"
                "🗣 审核通过后，Bot 会通知您\n"
                "⏳ 请耐心等待...…"
            ),
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
        data = await request.json()
        logging.info(f"收到Webhook更新: {data}")
        await app.update_queue.put(Update.de_json(data, app.bot))
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
