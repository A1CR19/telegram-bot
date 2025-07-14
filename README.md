# Telegram 油卡自助机器人

## 💡 功能
- 欢迎图 + 菜单按钮
- 用户点击按钮获取卡信息
- 客服指引
- 支持 Webhook 部署

## 🚀 部署到 Render
1. Fork 本仓库
2. 前往 https://render.com 新建 Web Service
3. 设置环境变量：
   - `TELEGRAM_BOT_TOKEN`：你的 bot token
4. 部署成功后，Render 会自动设置 webhook

## 📦 本地运行
```bash
export TELEGRAM_BOT_TOKEN=你的token
python bot.py
