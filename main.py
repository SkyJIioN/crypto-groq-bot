import os
import logging 
from fastapi import FastAPI, Request
from telegram import Update, Bot 
from telegram.ext import Application, CommandHandler, ContextTypes 
from groq import Groq 
import uvicorn

Logging

logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(name)

Env variables

BOT_TOKEN = os.getenv("BOT_TOKEN") 
GROQ_API_KEY = os.getenv("GROQ_API_KEY") WEBHOOK_SECRET_PATH = f"/webhook"

FastAPI app

app = FastAPI()

Telegram app

app_telegram = Application.builder().token(BOT_TOKEN).build()

Groq client

groq_client = Groq(api_key=GROQ_API_KEY)

/start command

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("Привіт! Надішли мені запитання по крипті.")

/ask command

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE): query = ' '.join(context.args) if not query: await update.message.reply_text("Будь ласка, надай запит.") return

try:
    chat_completion = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "Ти асистент по криптовалютах."},
            {"role": "user", "content": query},
        ]
    )
    reply = chat_completion.choices[0].message.content
    await update.message.reply_text(reply)
except Exception as e:
    logger.error(f"Groq error: {e}")
    await update.message.reply_text("Помилка обробки запиту.")

Add handlers

app_telegram.add_handler(CommandHandler("start", start)) app_telegram.add_handler(CommandHandler("ask", ask))

FastAPI endpoint for Telegram Webhook

@app.post(WEBHOOK_SECRET_PATH) async def telegram_webhook(request: Request): data = await request.json() update = Update.de_json(data, Bot(BOT_TOKEN)) await app_telegram.process_update(update) return {"status": "ok"}

Запуск через uvicorn

if name == "main": port = int(os.getenv("PORT", 10000)) uvicorn.run("main:app", host="0.0.0.0", port=port)

