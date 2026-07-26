import pandas as pd
import requests
from datetime import datetime
import os
import time
from datetime import datetime

# 1. Fetch live rates from AwesomeAPI com tratamento de Rate Limit (429)
url = "https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL,GBP-BRL,CNY-BRL,JPY-BRL"
headers = {"User-Agent": "CurrenFluxApp/1.0"}

response = None
max_retries = 3

for attempt in range(max_retries):
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        response = res.json()
        break
    elif res.status_code == 429:
        print(f"Rate limit atingido (429). Tentativa {attempt + 1} de {max_retries}. Aguardando 15 segundos...")
        time.sleep(15)
    else:
        res.raise_for_status()

if not response or not isinstance(response, dict):
    raise RuntimeError(f"Não foi possível obter os dados da API. Resposta final: {res.text}")

today = datetime.now().strftime("%Y-%m-%d")

# Estruturar nova linha
new_data = {"date": today}
currencies = ["USD", "EUR", "GBP", "CNY", "JPY"]

for curr in currencies:
    key_found = None
    for k in response.keys():
        if k.upper().startswith(curr):
            key_found = k
            break
    
    if key_found:
        new_data[curr] = float(response[key_found]["bid"])
    else:
        raise KeyError(f"Chave para {curr} não encontrada na resposta: {response}")

# 2. Append/Update history CSV
history_file = "fx_history.csv"

if os.path.exists(history_file):
    df_hist = pd.read_csv(history_file)
    # Remove entry if updated today already, then append
    df_hist = df_hist[df_hist["date"] != today]
    df_hist = pd.concat([df_hist, pd.DataFrame([new_data])], ignore_index=True)
else:
    df_hist = pd.DataFrame([new_data])

df_hist.sort_values("date", ascending=True, inplace=True)
df_hist.to_csv(history_file, index=False)

# 3. Calculate % Variations
latest = df_hist.iloc[-1]

# Set lookback dates dynamically based on available history
def get_variation(df, days_back):
    if len(df) <= days_back:
        old_val = df.iloc[0]
    else:
        old_val = df.iloc[-(days_back + 1)]
    return old_val

weekly_ref = get_variation(df_hist, 7)
monthly_ref = get_variation(df_hist, 30)

summary = []
for curr in currencies:
    current_rate = latest[curr]
    w_rate = weekly_ref[curr]
    m_rate = monthly_ref[curr]

    var_w = ((current_rate - w_rate) / w_rate) * 100
    var_m = ((current_rate - m_rate) / m_rate) * 100

    trend = "↑" if var_w > 0 else ("↓" if var_w < 0 else "→")

    summary.append({
        "Currency": curr,
        "Rate (BRL)": round(current_rate, 4),
        "Weekly %": f"{var_w:+.2f}%",
        "Monthly %": f"{var_m:+.2f}%",
        "Trend": trend
    })

# 4. Export Dashboard CSV
df_summary = pd.DataFrame(summary)
df_summary.to_csv("fx_dashboard.csv", index=False)

print(f"Updated successfully for {today}!")