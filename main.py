import os
import logging
import requests
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# 🔐 Токен Telegram
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set in environment variables.")

bot = Bot(token=TOKEN)
app = FastAPI()

# 🔧 Логування
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# 🤖 Telegram Application
app_telegram = Application.builder().token(TOKEN).build()


# ✅ Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привіт! Надішли /analyze для аналізу BTC/USDT.")


# 📊 Команда /analyze
async def handle_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Отримуємо дані з CoinGecko API
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": "bitcoin", "vs_currencies": "usd"}
        res = requests.get(url, params=params)

        if res.status_code != 200:
            raise Exception("Не вдалося отримати дані з CoinGecko")

        price = res.json()["bitcoin"]["usd"]

        # Простий аналіз (умовний)
        entry = price * 0.995
        exit = price * 1.015

        response = (
            f"🔍 Поточна ціна BTC: ${price:.2f}\n"
            f"📈 Точка входу: ${entry:.2f}\n"
            f"📉 Точка виходу: ${exit:.2f}"
        )

        await update.message.reply_text(response)

    except Exception as e:
        logging.error(f"Помилка в аналізі: {e}")
        await update.message.reply_text("❌ Сталася помилка при аналізі.")


# ⚠️ Обробка помилок
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error(msg="Виняток при обробці оновлення:", exc_info=context.error)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("⚠️ Виникла помилка, спробуй ще раз пізніше.")


# 📥 Обробка звичайних повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Напиши /analyze для аналізу BTC/USDT.")


# 📌 Реєстрація хендлерів
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CommandHandler("analyze", handle_analyze))
app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app_telegram.add_error_handler(error_handler)


# 🌐 Webhook endpoint
@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot)
    await app_telegram.process_update(update)
    return {"ok": True}


# 🚀 Старт при запуску
@app.on_event("startup")
async def startup():
    logging.info("Запуск Telegram-бота...")
    await app_telegram.initialize()
    await app_telegram.start()
    logging.info("Бот готовий!")


@app.on_event("shutdown")
async def shutdown():
    logging.info("Зупинка бота...")
    await app_telegram.stop()
    await app_telegram.shutdown()