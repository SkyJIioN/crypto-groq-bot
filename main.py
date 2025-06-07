import requests  # переконайся, що імпорт стоїть на початку файлу

async def handle_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Аналізую...")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "Ти асистент-аналітик криптовалют."},
            {"role": "user", "content": "Зроби аналіз ринку BTC/USDT на сьогоднішній день."}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
        else:
            reply = f"❌ Помилка Groq API:\n{response.status_code}\n{response.text}"
    except Exception as e:
        reply = f"❌ Внутрішня помилка:\n{e}"

    await update.message.reply_text(reply)