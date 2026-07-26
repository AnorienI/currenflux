import pandas as pd
import requests
from datetime import datetime
import os

# 1. Fetch live rates from AwesomeAPI
url = "https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL,GBP-BRL,CNY-BRL,JPY-BRL"
response = requests.get(url).json()

today = datetime.now().strftime("%Y-%m-%d")

# Structure new row
new_data = {"date": today}
currencies = ["USD", "EUR", "GBP", "CNY", "JPY"]

for curr in currencies:
    # AwesomeAPI combines pair names into 'USDBRL', 'EURBRL', etc.
    key = f"{curr}BRL"
    
    if key in response:
        new_data[curr] = float(response[key]["bid"])
    elif f"{curr}-BRL" in response:
        new_data[curr] = float(response[f"{curr}-BRL"]["bid"])
    else:
        # Fallback in case of lowercase key returning
        lowered_dict = {k.upper(): v for k, v in response.items()}
        new_data[curr] = float(lowered_dict[key]["bid"])

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