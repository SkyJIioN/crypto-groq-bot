import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters
)
import logging
import asyncio
import openai

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ключі з env
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# FastAPI застосунок
app = FastAPI()

# Ініціалізація Telegram Application
app_telegram = Application.builder().token(BOT_TOKEN).build()

# ✅ Обробник команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Надішли мені повідомлення, і я відповім через Groq AI.")

async def handle_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Будь ласка, введіть текст для аналізу після команди /analyze.")
        return

    text = " ".join(context.args)
    response = groq.chat.completions.create(
        messages=[
            {"role": "system", "content": "Ти крипто-асистент. Аналізуй повідомлення."},
            {"role": "user", "content": text},
        ],
        model="mixtral-8x7b-32768",
    )
    await update.message.reply_text(response.choices[0].message.content)

# ✅ Обробник звичайних повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    # Виклик LLM через Groq API (OpenAI сумісний)
    response = openai.ChatCompletion.create(
        model="mixtral-8x7b-32768",
        messages=[{"role": "user", "content": user_message}],
        api_key=GROQ_API_KEY,
    )

    reply_text = response["choices"][0]["message"]["content"]
    await update.message.reply_text(reply_text)

# Реєстрація обробників
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CommandHandler("analyze", handle_analyze))
app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# FastAPI endpoint для webhook
@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, app_telegram.bot)
    await app_telegram.process_update(update)
    return {"status": "ok"}

# Запуск Telegram-бота при старті FastAPI
@app.on_event("startup")
async def on_startup():
    asyncio.create_task(app_telegram.initialize())
    logger.info("Telegram bot initialized")

# Опціональний кореневий маршрут
@app.get("/")
def read_root():
    return {"message": "Бот працює. Webhook на /webhook"}