import os
import requests
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update
import logging
from groq import Groq

TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEBHOOK_SECRET_PATH = "/webhook"

bot = Bot(token=TOKEN)
app = FastAPI()

app_telegram = Application.builder().token(TOKEN).build()

# --- Отримання актуальної ціни BTC з CoinGecko ---
def get_btc_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": "usd"}
    response = requests.get(url, params=params)
    return response.json()["bitcoin"]["usd"]

# --- Формування запиту до Groq ---
def ask_groq_about_btc(price):
    groq = Groq(api_key=GROQ_API_KEY)
    prompt = (
        f"Ти — досвідчений криптоаналітик. Поточна ціна Bitcoin — {price} USD.\n"
        f"Напиши короткий аналіз ринку. Дай ймовірну точку входу та виходу. Без води."
    )
    chat_completion = groq.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "Ти допомагаєш трейдерам з аналізом ринку."},
            {"role": "user", "content": prompt},
        ]
    )
    return chat_completion.choices[0].message.content

# --- Обробники Telegram ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Надішли /analyze щоб отримати аналіз ринку BTC.")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = get_btc_price()
    analysis = ask_groq_about_btc(price)
    await update.message.reply_text(f"Поточна ціна BTC: {price} USD\n\n{analysis}")

# --- Додати обробники ---
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CommandHandler("analyze", analyze))
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error(msg="Exception while handling an update:", exc_info=context.error)

# --- FastAPI інтеграція ---
@app.post(WEBHOOK_SECRET_PATH)
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot)
    await app_telegram.process_update(update)
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "Crypto bot is running!"}
Application:
app_telegram.add_error_handler(error_handler)
# --- Старт застосунку ---
@app.on_event("startup")
async def startup_event():
    await app_telegram.initialize()
    print("Bot initialized")

@app.on_event("shutdown")
async def shutdown_event():
    await app_telegram.shutdown()
    print("Bot shutdown")
