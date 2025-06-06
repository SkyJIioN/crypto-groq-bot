import os
import logging
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes,filters
from groq import Groq
import asyncio

# Logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

WEBHOOK_SECRET_PATH = "/webhook"

# FastAPI app
app = FastAPI()

# Telegram app
bot = Bot(token=BOT_TOKEN)
app_telegram = Application.builder().token(BOT_TOKEN).build()

# GROQ client
groq_client = Groq(api_key=GROQ_API_KEY)

# Telegram command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Надішли будь-яке питання про криптовалюту.")

# Обробка текстових повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    response = groq_client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": "Ти криптоасистент."},
            {"role": "user", "content": question}
        ]
    )
    answer = response.choices[0].message.content
    await update.message.reply_text(answer)

# Команди
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CommandHandler("help", start))
app_telegram.add_handler(CommandHandler("info", start))
app_telegram.add_handler(CommandHandler("ask", handle_message))

# Обробка будь-якого тексту, який не є командою
app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# FastAPI startup
@app.on_event("startup")
async def startup():
    await app_telegram.initialize()
    await app_telegram.start()
    await bot.set_webhook(f"{WEBHOOK_URL}")

@app.on_event("shutdown")
async def shutdown():
    await app_telegram.stop()
    await app_telegram.shutdown()

# Webhook route
@app.post(WEBHOOK_SECRET_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await app_telegram.process_update(update)
    return {"ok": True}

# Кореневий маршрут
@app.get("/")
async def root():
    return {"message": "Бот працює ✅"}