import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# 日志配置
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 处理 /start 命令
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logging.info("收到 /start 命令")
        keyboard = [['🛒 油卡 *1 张', '🛒 油卡 *5 张']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("欢迎使用油卡自助购买系统，请选择您要购买的油卡数量：", reply_markup=reply_markup)
    except Exception as e:
        logging.error(f"/start 处理失败: {e}")

# 处理普通消息
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.strip()
        logging.info(f"收到用户消息: {text}")

        if "油卡" in text:
            quantity = ''.join(filter(str.isdigit, text))
            price_per = 830
            total = int(quantity or 1) * price_per
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
        else:
            await update.message.reply_text(f"收到未处理的消息：{text}")
    except Exception as e:
        logging.error(f"处理消息时出错: {e}")
        await update.message.reply_text("⚠️ 出现错误，稍后再试或联系管理员")

# 主函数入口
if __name__ == '__main__':
    import asyncio

    TOKEN = os.getenv("BOT_TOKEN") or "8123986506:AAH6nmhU5J8Lm0M306sISf8GHwdERRpDpLA"
    PORT = int(os.environ.get("PORT", "10000"))  # Render 默认绑定到 10000 端口
    WEBHOOK_URL = f"https://telegram-bot-28w5.onrender.com/{TOKEN}"

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        async def main():
        await app.initialize()
        await app.bot.set_webhook(WEBHOOK_URL)
        logging.info(f"设置 webhook 到：{WEBHOOK_URL}")
        await app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=WEBHOOK_URL,
        )


    asyncio.run(main())
