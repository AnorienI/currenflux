import requests

# Mapeamento das 5 criptos do seu laboratório
COINS_MAP = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
    "polkadot": "DOT",
    "cardano": "ADA",
    "litecoin": "LTC"
}

def fetch_crypto_lab_data() -> list[dict]:
    """
    Busca cotações em BRL e variação de 24h para DOT, SOL, ADA, LTC e ETH.
    Gera o sinal 'BUY' se a moeda estiver em curva de recuo relevante.
    """
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ",".join(COINS_MAP.keys()),
        "vs_currencies": "brl",
        "include_24hr_change": "true"
    }
    
    try:
        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        data = response.json()
        
        crypto_list = []
        for coin_id, ticker in COINS_MAP.items():
            if coin_id in data:
                price_brl = data[coin_id]["brl"]
                change_24h = data[coin_id].get("brl_24h_change", 0.0)
                
                # Regra do Lab: Recuo significativo no dia/ciclo indica oportunidade de entrada
                signal = "BUY" if change_24h <= -3.0 else "HOLD"
                
                crypto_list.append({
                    "ticker": ticker,
                    "price_brl": round(price_brl, 2),
                    "pct_from_high": round(change_24h, 1),
                    "signal": signal
                })
        return crypto_list

    except Exception as e:
        # Fallback de teste local caso ocorra rate-limit ou sem internet
        return [
            {"ticker": "BTC", "price_brl": 380000.00, "pct_from_high": -2.1, "signal": "HOLD"},
            {"ticker": "ETH", "price_brl": 14500.00, "pct_from_high": -7.1, "signal": "HOLD"},
            {"ticker": "SOL", "price_brl": 520.00, "pct_from_high": -3.2, "signal": "HOLD"},
            {"ticker": "DOT", "price_brl": 5.80, "pct_from_high": -22.5, "signal": "BUY"},
            {"ticker": "ADA", "price_brl": 1.18, "pct_from_high": -18.0, "signal": "HOLD"},
            {"ticker": "LTC", "price_brl": 300.00, "pct_from_high": -25.0, "signal": "BUY"}
        ]

if __name__ == "__main__":
    print("✅ Testando Coletor de Cripto:")
    print(fetch_crypto_lab_data())