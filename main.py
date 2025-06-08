import os
import logging
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, ContextTypes,
    MessageHandler, filters
)
from services.market_data import get_price

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET_PATH = "/webhook"

app = FastAPI()
app_telegram = Application.builder().token(TOKEN).build()

# --- Команди ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Вітаю! Напиши /analyze щоб отримати аналіз.")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prices = get_price(["BTC", "ETH"])
    btc = prices.get("BTC", "н/д")
    eth = prices.get("ETH", "н/д")
    response = (
        f"📊 Аналіз ринку:\n"
        f"BTC: ${btc}\nETH: ${eth}\n\n"
        f"🔽 Можлива точка входу: нижче ${float(btc)-100}\n"
        f"🔼 Точка виходу: +5-10% від входу"
    )
    await update.message.reply_text(response)

# --- Обробка помилок ---
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Виняток при обробці оновлення: {context.error}")

# --- FastAPI endpoint ---
@app.post(WEBHOOK_SECRET_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, app_telegram.bot)
    await app_telegram.process_update(update)
    return {"status": "ok"}

# --- Запуск ---
@app.on_event("startup")
async def on_startup():
    await app_telegram.initialize()
    await app_telegram.bot.set_webhook(f"{os.getenv('WEBHOOK_URL')}{WEBHOOK_SECRET_PATH}")
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CommandHandler("analyze", analyze))
    app_telegram.add_error_handler(error_handler)
    await app_telegram.start()

@app.on_event("shutdown")
async def on_shutdown():
    await app_telegram.stop()
