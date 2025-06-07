import os
import logging
import requests
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET_PATH = "/webhook"

# Створення FastAPI застосунку
app = FastAPI()
bot = Bot(token=TOKEN)

# Створення Telegram application
app_telegram = Application.builder().token(TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Я крипто-бот. Надішли /analyze для аналізу.")

# Команда /analyze
async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price", params={
            "ids": "bitcoin",
            "vs_currencies": "usd"
        })

        data = response.json()
        price = data["bitcoin"]["usd"]

        # Простий сигнал
        entry = price * 0.98
        exit = price * 1.02

        text = f"📈 Поточна ціна BTC: ${price:.2f}\n🎯 Вхід: ${entry:.2f}\n🏁 Вихід: ${exit:.2f}"
        await update.message.reply_text(text)

    except Exception as e:
        logger.error(f"Помилка аналізу: {e}")
        await update.message.reply_text("⚠️ Виникла помилка при аналізі.")

# Обробник повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Надішли /analyze для аналізу BTC.")

# Додавання хендлерів
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CommandHandler("analyze", analyze))
app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Webhook endpoint (важливо!)
@app.post(WEBHOOK_SECRET_PATH)
async def telegram_webhook(req: Request):
    try:
        update = Update.de_json(await req.json(), bot)
        await app_telegram.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Виняток при обробці оновлення: {e}")
        return {"status": "error"}

# Ping для перевірки
@app.get("/")
async def root():
    return {"message": "Bot is running."}