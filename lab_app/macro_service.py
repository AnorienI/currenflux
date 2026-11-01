import sqlite3
import glob
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_AGENTIC = BASE_DIR / "agentic_pipeline" / "currenflux.db"
DB_ROOT = BASE_DIR / "currenflux.db"

CURRENFLUX_DB = DB_AGENTIC if DB_AGENTIC.exists() else DB_ROOT

def _load_cb_rates_from_csv() -> pd.DataFrame:
    """Busca o histórico nos arquivos CSV caso a tabela cb_rates não exista no SQLite."""
    search_paths = [
        BASE_DIR / "agentic_pipeline" / "agentic2" / "agent_pipeline2" / "cb_rates_*.csv",
        BASE_DIR / "cb_rates_*.csv",
        BASE_DIR / "modules" / "cb_rates.csv"
    ]
    files = []
    for p in search_paths:
        files.extend(glob.glob(str(p)))
    
    if not files:
        return pd.DataFrame()
    
    # Carrega e concatena os arquivos encontrados
    return pd.concat([pd.read_csv(f) for f in sorted(files)], ignore_index=True)

def get_latest_macro_state() -> dict:
    """
    Lê o snapshot macroeconômico usando SQLite e fallback para CSVs históricos.
    """
    if not CURRENFLUX_DB.exists():
        raise FileNotFoundError(f"Erro Crítico: Banco de dados não encontrado em '{CURRENFLUX_DB}'.")

    conn = sqlite3.connect(CURRENFLUX_DB)
    try:
        # 1. Cotações FX
        fx_df = pd.read_sql_query("SELECT * FROM fx_dashboard", conn)
        if fx_df.empty:
            raise ValueError("Erro de Leitura: A tabela 'fx_dashboard' está vazia.")
            
        usd_mask = fx_df["par"].astype(str).str.upper().isin(["USD/BRL", "USDBRL", "USD"])
        usd_row = fx_df[usd_mask]
        
        if usd_row.empty:
            pares_encontrados = fx_df["par"].unique().tolist()
            raise ValueError(f"Erro de Dados: Par USD/BRL não encontrado em 'fx_dashboard'. Pares presentes: {pares_encontrados}")

        usd_brl = float(usd_row["cotacao"].iloc[-1])

        eur_mask = fx_df["par"].astype(str).str.upper().isin(["EUR/BRL", "EURBRL", "EUR"])
        eur_row = fx_df[eur_mask]
        eur_brl = float(eur_row["cotacao"].iloc[-1]) if not eur_row.empty else round(usd_brl * 1.08, 4)

        # 2. Taxas dos Bancos Centrais (SQLite com fallback para CSV)
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
        
        if "cb_rates" in tables:
            cb_df = pd.read_sql_query("SELECT * FROM cb_rates", conn)
        else:
            cb_df = _load_cb_rates_from_csv()

        bcb, fed, ecb = 13.75, 3.75, 2.50

        if not cb_df.empty:
            bank_col = "central_bank" if "central_bank" in cb_df.columns else ("Country" if "Country" in cb_df.columns else None)
            rate_col = "rate_value" if "rate_value" in cb_df.columns else ("Rate" if "Rate" in cb_df.columns else None)
            
            if bank_col and rate_col:
                bcb_match = cb_df[cb_df[bank_col].astype(str).str.upper().isin(["BCB", "BRA", "BRL"])][rate_col]
                fed_match = cb_df[cb_df[bank_col].astype(str).str.upper().isin(["FED", "USA", "USD"])][rate_col]
                ecb_match = cb_df[cb_df[bank_col].astype(str).str.upper().isin(["ECB", "EUR"])][rate_col]
                
                if not bcb_match.empty: bcb = float(bcb_match.iloc[-1])
                if not fed_match.empty: fed = float(fed_match.iloc[-1])
                if not ecb_match.empty: ecb = float(ecb_match.iloc[-1])

        brl_status = "BRL Forte" if usd_brl < 5.00 else "BRL Pressionado"

        return {
            "fed_rate": fed,
            "ecb_rate": ecb,
            "bcb_rate": bcb,
            "usd_brl": round(usd_brl, 4),
            "eur_brl": round(eur_brl, 4),
            "brl_strength_index": f"{brl_status} (USD @ R$ {usd_brl:.2f})"
        }
    finally:
        conn.close()

if __name__ == "__main__":
    try:
        data = get_latest_macro_state()
        print("✅ Leitura do CurrenFlux realizada com sucesso:")
        print(data)
    except Exception as e:
        print(f"❌ Erro: {e}")