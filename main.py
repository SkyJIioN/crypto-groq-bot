import os
import logging
import requests
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, ContextTypes, MessageHandler, filters
)
from dotenv import load_dotenv

# Завантажуємо токени
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# FastAPI
app = FastAPI()

# Telegram bot
app_telegram = Application.builder().token(BOT_TOKEN).build()

# Webhook шлях
WEBHOOK_PATH = "/webhook"

# Команда /start
async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привіт! Надішли /analyze щоб отримати аналіз ринку.")

from pybit.unified_trading import HTTP
import os

session = HTTP(
    testnet=False,
    api_key=os.getenv("BYBIT_API_KEY"),
    api_secret=os.getenv("BYBIT_API_SECRET")
)

async def handle_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        ticker = session.get_tickers(category="spot", symbol="BTCUSDT")["result"]["list"][0]
        last_price = ticker["lastPrice"]
        high_price = ticker["highPrice24h"]
        low_price = ticker["lowPrice24h"]
        volume = ticker["volume24h"]

        # Prompt для Groq
        prompt = (
            f"Аналіз ринку BTC/USDT:\n"
            f"- Поточна ціна: {last_price}\n"
            f"- Висока за 24г: {high_price}\n"
            f"- Низька за 24г: {low_price}\n"
            f"- Об'єм за 24г: {volume}\n\n"
            f"На основі цього, напиши короткий аналіз з конкретними точками входу/виходу."
        )

        response = groq.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "Ти криптоаналітик. Пиши коротко і ясно."},
                {"role": "user", "content": prompt},
            ]
        )

        result = response.choices[0].message.content
        await update.message.reply_text(result)

    except Exception as e:
        await update.message.reply_text("Сталася помилка при аналізі. Спробуйте пізніше.")
        print("Помилка:", e)

# Обробка тексту
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❗ Використай команду /analyze для аналізу ринку.")

# Додаємо хендлери
app_telegram.add_handler(CommandHandler("start", handle_start))
app_telegram.add_handler(CommandHandler("analyze", handle_analyze))
app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# FastAPI маршрут для Telegram webhook
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, app_telegram.bot)
    await app_telegram.process_update(update)
    return {"status": "ok"}

# Стартуємо застосунок Telegram
@app.on_event("startup")
async def startup():
    await app_telegram.initialize()
    await app_telegram.start()
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"
    await app_telegram.bot.set_webhook(webhook_url)

# Завершення роботи
@app.on_event("shutdown")
async def shutdown():
    await app_telegram.stop()
