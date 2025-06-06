# main.py
import os
import logging
import asyncio
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from groq import Groq

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Отримання змінних оточення
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Ініціалізація Telegram бота та FastAPI
bot = Bot(token=BOT_TOKEN)
app = FastAPI()
application = Application.builder().token(BOT_TOKEN).build()

# Groq клієнт
groq_client = Groq(api_key=GROQ_API_KEY)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привіт! Надішли команду /analyze, щоб отримати аналіз ринку.")

# Команда /analyze
async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = "Ціна BTC/USDT зараз 67000$. Чи варто входити в позицію на 1H графіку?"
    try:
        response = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "Ти досвідчений трейдер криптовалюти."},
                {"role": "user", "content": prompt},
            ]
        )
        answer = response.choices[0].message.content
        await update.message.reply_text(f"💡 Відповідь:{answer}")
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        await update.message.reply_text("❌ Сталася помилка при зверненні до Groq API.")

# Додавання хендлерів
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("analyze", analyze))

# FastAPI endpoint
@app.post("/webhook")
async def telegram_webhook(req: Request):
    try:
        data = await req.json()
        update = Update.de_json(data, bot)
        await application.initialize()
        await application.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error", "detail": str(e)}

# Головна сторінка
@app.get("/")
async def root():
    return {"message": "Crypto GROQ Bot is live!"}

# Запуск
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))