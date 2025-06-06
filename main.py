# main.py
import os
import logging
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import (
    Application, CommandHandler, ContextTypes
)

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = "/webhook"

bot = Bot(token=BOT_TOKEN)
application = Application.builder().token(BOT_TOKEN).build()
app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await application.initialize()
    await application.start()
    logging.info("Telegram application started.")

@app.on_event("shutdown")
async def on_shutdown():
    await application.stop()
    logging.info("Telegram application stopped.")

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return {"ok": True}

# Command handler for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот активний!")

application.add_handler(CommandHandler("start", start))