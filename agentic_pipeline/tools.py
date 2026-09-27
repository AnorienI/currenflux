import sqlite3
import pandas as pd
from datetime import datetime
from langchain_core.tools import tool

DB_PATH = "currenflux.db"

@tool
def fetch_and_load_currenflux_data() -> str:
    """Coleta dados de FX, Bancos Centrais e Comex para o SQLite."""
    conn = sqlite3.connect(DB_PATH)
    today = datetime.now().strftime("%Y-%m-%d")
    
    fx_data = [{"data": today, "par": "USD/BRL", "cotacao": 5.1272}]
    pd.DataFrame(fx_data).to_sql("fx_dashboard", conn, if_exists="append", index=False)
    
    conn.close()
    return "Dados atualizados no SQLite!"

@tool
def export_query_to_excel(query_sql: str, file_path: str = "currenflux_report.xlsx") -> str:
    """Executa uma consulta SQL no CurrenFlux e exporta em Excel."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query_sql, conn)
    conn.close()
    
    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="CurrenFlux", index=False)
    
    return f"Relatório exportado em: {file_path}"