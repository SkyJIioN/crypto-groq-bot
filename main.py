import os
import logging
import requests
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from groq import Groq
from fastapi import FastAPI, 
Request
import uvicorn

# Логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI
web_app = FastAPI()

# Токени
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEBHOOK_SECRET = "securetoken123"

# Telegram
bot = Bot(token=BOT_TOKEN)
app = Application.builder().token(BOT_TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Надішли /analyze щоб отримати аналіз ринку.")

# Функція отримання ціни BTC
def get_btc_price():
    url = "https://api.bybit.com/v2/public/tickers?symbol=BTCUSDT"
    try:
        response = requests.get(url)
        price = float(response.json()["result"][0]["last_price"])
        return round(price, 2)
    except Exception as e:
        logger.error(f"Помилка отримання ціни BTC: {e}")
        return None

# Команда /analyze
async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = get_btc_price()
    if price is None:
        await update.message.reply_text("Не вдалося отримати ціну BTC.")
        return

    prompt = f"Ціна BTC/USDT зараз {price}$. Чи варто входити в позицію на 1H графіку? Дай коротку пораду українською."

    client = Groq(api_key=GROQ_API_KEY)
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="mixtral-8x7b-32768"
    )

    reply = chat_completion.choices[0].message.content.strip()
    await update.message.reply_text(reply)

# Обробники команд
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("analyze", analyze))

# FastAPI endpoint для Telegram webhook
@web_app.post(f"/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
        return {"status": "forbidden"}
    data = await request.json()
    update = Update.de_json(data, bot)
    await app.update_queue.put(update)
    return {"status": "ok"}

# Запуск вебсервера
if __name__ == "__main__":
    import asyncio
    async def run():
        await app.initialize()
        await app.start()
        await bot.set_webhook(
            url=f"{WEBHOOK_URL}/{BOT_TOKEN}",
            secret_token=WEBHOOK_SECRET,
        )
        config = uvicorn.Config("main:web_app", host="0.0.0.0", port=10000, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
        await app.stop()
    asyncio.run(run())
