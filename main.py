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

# Команда /analyze
async def handle_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Аналізую...")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "Ти асистент-аналітик криптовалют."},
            {"role": "user", "content": "Зроби аналіз ринку BTC/USDT на 1 нодину Українською, з точкою входу і виходу"}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
        else:
            reply = f"❌ Groq API помилка: {response.status_code}\n{response.text}"
    except Exception as e:
        reply = f"❌ Внутрішня помилка:\n{e}"

    await update.message.reply_text(reply)

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
