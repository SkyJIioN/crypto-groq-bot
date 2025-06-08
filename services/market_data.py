import requests

def get_price(symbols):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ",".join([s.lower() for s in symbols]),
        "vs_currencies": "usd"
    }
    response = requests.get(url, params=params)
    data = response.json()
    return {s: data.get(s.lower(), {}).get("usd", "н/д") for s in symbols}
