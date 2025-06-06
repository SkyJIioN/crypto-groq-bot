import os
import logging
import traceback
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from groq import Groq

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(BOT_TOKEN)
application = Application.builder().token(BOT_TOKEN).build()

logging.basicConfig(level=logging.INFO)

# === Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Надішли /analyze, щоб отримати аналіз BTC.")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    btc_price = get_btc_price()
    prompt = (
        f"Ціна BTC/USDT зараз {btc_price}$. "
        "Чи варто входити в позицію на 1H графіку? "
        "Дай короткий трейдерський аналіз."
    )
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="mixtral-8x7b-32768",
    )
    answer = response.choices[0].message.content
    await update.message.reply_text(answer)

def get_btc_price():
    import requests
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    response = requests.get(url)
    return round(float(response.json()["price"]), 2)

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("analyze", analyze))

# === FastAPI route ===
@app.post(f"/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, bot)
        await application.process_update(update)
    except Exception as e:
        print("❌ Помилка у вебхуці:", e)
        traceback.print_exc()
    return {"status": "ok"}
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))  # Render задає порт у $PORT
    uvicorn.run("main:app", host="0.0.0.0", port=port)

# === Ініціалізація один раз при запуску ===
@app.on_event("startup")
async def on_startup():
    await application.initialize()
    await bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    print(f"✅ Webhook встановлено: {WEBHOOK_URL}/{BOT_TOKEN}")