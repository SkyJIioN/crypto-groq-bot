import os
import logging
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from groq import Groq
import requests

# Логування
logging.basicConfig(level=logging.INFO)

# Змінні середовища
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Наприклад: https://crypto-groq-bot.onrender.com
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Telegram
bot = Bot(token=BOT_TOKEN)
app_telegram = Application.builder().token(BOT_TOKEN).build()

# FastAPI
app = FastAPI()

# ----------- ФУНКЦІЇ ----------

def get_btc_price():
    try:
        res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")
        return float(res.json()["price"])
    except Exception as e:
        logging.error(f"Помилка отримання ціни BTC: {e}")
        return "недоступна"

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    btc_price = get_btc_price()
    user_message = (
        f"Ціна BTC/USDT: {btc_price}$\n"
        "Чи варто входити в позицію на 1H графіку?"
    )

    client = Groq(api_key=GROQ_API_KEY)
    chat_completion = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[{"role": "user", "content": user_message}]
    )

    answer = chat_completion.choices[0].message.content
    await update.message.reply_text(answer)

# ----------- ОБРОБНИКИ ----------

@app.post(f"/{BOT_TOKEN}")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot)
    await app_telegram.initialize()
    await app_telegram.process_update(update)
    return {"ok": True}

@app.get("/")
def root():
    return {"message": "Bot is running"}

# ----------- СТАРТ ----------

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    app_telegram.add_handler(CommandHandler("analyze", analyze))
    uvicorn.run("main:app", host="0.0.0.0", port=port)