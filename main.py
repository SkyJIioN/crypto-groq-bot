import os
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import asyncio
import groq

TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WEBHOOK_SECRET_PATH = "/webhook"
BASE_WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL")

bot = Bot(token=TOKEN)
app = FastAPI()
app_telegram = Application.builder().token(TOKEN).build()

# === Команди Telegram ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Надішли /analyze ваш запит для аналізу крипторинку.")

async def handle_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Будь ласка, введіть текст після команди /analyze")
        return

    text = " ".join(context.args)
    try:
        client = groq.Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "Ти досвідчений аналітик криптовалют. Дай точний і короткий аналіз."},
                {"role": "user", "content": text},
            ]
        )
        answer = response.choices[0].message.content
        await update.message.reply_text(answer)
    except Exception as e:
        await update.message.reply_text(f"Сталася помилка під час аналізу: {e}")

# === Додати хендлери ===
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CommandHandler("analyze", handle_analyze))

# === FastAPI маршрути ===
@app.on_event("startup")
async def startup():
    asyncio.create_task(app_telegram.initialize())
    await app_telegram.start()
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_SECRET_PATH}")
    print("Webhook встановлено")

@app.on_event("shutdown")
async def shutdown():
    await app_telegram.stop()

@app.post(WEBHOOK_SECRET_PATH)
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot)
    await app_telegram.process_update(update)
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Бот працює"}
