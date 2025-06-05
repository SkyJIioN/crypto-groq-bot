import os
import logging
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from groq import Groq
import requests
from fastapi import FastAPI, Request
import uvicorn

BOT_TOKEN = os.getenv("BOT_TOKEN") 
WEBHOOK_URL = os.getenv("WEBHOOK_URL") 
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = Bot(token=BOT_TOKEN) 
app = FastAPI()

telegram_app = Application.builder().token(BOT_TOKEN).build()

Логування

logging.basicConfig(level=logging.INFO)

GROQ 
клієнт

client = Groq(api_key=GROQ_API_KEY)

def get_analysis(): 
prompt = "Ціна BTC/USDT зараз 67,000$. Чи варто входити в позицію на 1H графіку? Відповідь коротко." 
response = client.chat.completions.create( model="mixtral-8x7b-32768", 
messages=[{"role": "user", "content": prompt}], temperature=0.3, ) return response.choices[0].message.content.strip()

Обробка команди

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE): analysis = get_analysis() await update.message.reply_text(analysis)

telegram_app.add_handler(CommandHandler("analyze", analyze))

Прийом оновлень від Telegram

@app.post(f"/{BOT_TOKEN}") async def handle_update(request: Request): data = await request.json() update = Update.de_json(data, bot) await telegram_app.process_update(update)

if name == "main": telegram_app.run_webhook( listen="0.0.0.0", port=int(os.environ.get("PORT", 5000)), webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}", secret_token="securetoken123" )

