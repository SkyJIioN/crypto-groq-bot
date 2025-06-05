import os
import logging
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from groq import Groq

# Логування
logging.basicConfig(level=logging.INFO)

# API ключі
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Telegram app
bot = Bot(BOT_TOKEN)
app_telegram = Application.builder().token(BOT_TOKEN).build()

# FastAPI app
app = FastAPI()

# GROQ
groq_client = Groq(api_key=GROQ_API_KEY)

def get_btc_price():
    # Псевдоціна, заміни на реальний API якщо треба
    return "67000"

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привіт! Надішли команду /analyze для аналізу ринку.")

# Команда /analyze
async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    btc_price = get_btc_price()
    prompt = f"Ціна BTC/USDT зараз {btc_price}$. Чи варто входити в позицію на 1H графіку? Коротко українською."

    chat_completion = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}]
    )
    reply = chat_completion.choices[0].message.content
    await update.message.reply_text(reply)

# Додаємо обробники
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CommandHandler("analyze", analyze))

# Webhook шлях
@app.post(f"/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await app_telegram.process_update(update)
    return {"status": "ok"}

# Root (не обов'язково)
@app.get("/")
async def root():
    return {"message": "✅ Crypto Bot is running"}