import requests

# ВСТАВ СВІЙ GROQ API KEY сюди
GROQ_API_KEY = "тут_твій_groq_api_key"

def get_btc_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    return float(data["bitcoin"]["usd"])

def ask_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

# Основна логіка
btc_price = get_btc_price()
print(f"Ціна BTC/USDT: ${btc_price}")

prompt = (
    f"Ціна BTC/USDT зараз {btc_price}$. "
    "Чи варто входити в позицію на 1H графіку? "
    "Дай коротку відповідь (до 3 речень), аргументуй технічно. "
    "Відповідай українською мовою."
)

answer = ask_groq(prompt)
print("\n📊 Відповідь ШІ:")
print(answer)
