### 1. Requirements & Setup
* **Python:** 3.9+
* **Dependencies:** `pandas`, `requests`

```bash
# Install dependencies
pip install pandas requests
```

### 2. Execution
Run the full orchestrated pipeline from the root directory:

```bash
python3 main.py
```

*Note: Modules can also be run independently for debugging (e.g., `python3 modules/fetch_fx.py`).*

---

## 📊 Data Behavior & Output

* **`fx_dashboard.csv`:** Appends new daily entries and deduplicates by date on re-runs.
* **`cb_rates.csv`:** Overwritten per run with the latest policy rate snapshot.
* **`trade_data.csv`:** Overwritten per run with the most recent monthly trade balance figures.

> **Resilience Note:** Each fetch task is wrapped in exception handling (`try/except`) and logged. If an API times out, the error is caught and skipped without interrupting the rest of the pipeline.

---

## 📋 Sample Run Output

```text
2026-07-29 18:38:27,381 - INFO - Starting CurrenFlux Data Pipeline...
=== Atualizando Dados de Câmbio (FX) ===
  └─ USD/BRL: R$ 5.1272
  └─ EUR/BRL: R$ 5.8720
  └─ GBP/BRL: R$ 6.8523
  └─ CNY/BRL: R$ 0.7570
  └─ JPY/BRL: R$ 0.0314
-> Atualizado com sucesso em fx_dashboard.csv para 2026-07-29!

2026-07-29 18:38:27,578 - INFO - FX Data updated successfully.
=== Atualizando Dados dos Bancos Centrais ===
[BCB - Brasil] Selic Meta: 14.25% (Data: 05/08/2026)
[FED - EUA] Fed Funds Rate: 3.63% (Data: 2026-06-01)
[BCE - Eurozona] Deposit Facility Rate: 2.25% (Data: 2026-07-29)
-> Salvo com sucesso em cb_rates.csv

2026-07-29 18:38:31,091 - INFO - Central Bank rates updated successfully.
=== Atualizando Dados de Comércio Exterior ===
[Brasil - Comex] Mês de Referência: 01/06/2026
  └─ Exportações: US$ 8,830.30 Mi
  └─ Importações: US$ 36,417.30 Mi
  └─ Saldo Comercial: US$ 27,587.10 Mi
-> Salvo com sucesso em trade_data.csv

2026-07-29 18:38:33,154 - INFO - Trade Data updated successfully.
```

---

## 💡 Roadmap Ideas
* [ ] Convert `cb_rates` and `trade_data` to append historical time series.
* [ ] Automate daily runs using GitHub Actions or Cron.
* [ ] Implement data validation (range checks and stale date warnings).
* [ ] Export outputs directly to a SQL database (MariaDB / PostgreSQL).