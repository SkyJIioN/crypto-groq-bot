import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from groq import Groq

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = ApplicationBuilder().token(BOT_TOKEN).build()
client = Groq(api_key=GROQ_API_KEY)

def get_btc_price():
    url = "https://api.bybit.com/v2/public/tickers?symbol=BTCUSDT"
    response = requests.get(url)
    data = response.json()
    return float(data["result"][0]["last_price"])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Надішли /analyze, щоб отримати поради по BTC.")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = get_btc_price()
    prompt = f"Ціна BTC/USDT зараз {price}$. Чи варто входити в позицію на 1H графіку? Відповідай коротко українською."

    reply = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[{"role": "user", "content": prompt}]
    )

    await update.message.reply_text(reply.choices[0].message.content)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("analyze", analyze))

if __name__ == "__main__":
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}",
        secret_token="mysecret123"
    )
