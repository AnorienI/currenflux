import os
import sqlite3
import pandas as pd
import requests
from datetime import datetime

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_ollama import ChatOllama

# Database name for CurrenFlux
DB_PATH = "currenflux.db"

# ---------------------------------------------------------
# ETAPA 1: Ferramenta de Ingestão de Dados (CurrenFlux Fetcher)
# ---------------------------------------------------------
@tool
def fetch_and_load_currenflux_data() -> str:
    """
    Coleta dados atualizados de FX (câmbio), taxas de Bancos Centrais e balança comercial (Comex) 
    e os salva nas tabelas SQLite ('fx_dashboard', 'cb_rates', 'trade_data').
    """
    conn = sqlite3.connect(DB_PATH)
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 1. Dados de Câmbio (FX) - Exemplo de Estrutura
    fx_data = [
        {"data": today, "par": "USD/BRL", "cotacao": 5.1272},
        {"data": today, "par": "EUR/BRL", "cotacao": 5.8720},
        {"data": today, "par": "GBP/BRL", "cotacao": 6.8523},
        {"data": today, "par": "CNY/BRL", "cotacao": 0.7570},
        {"data": today, "par": "JPY/BRL", "cotacao": 0.0314}
    ]
    df_fx = pd.DataFrame(fx_data)
    df_fx.to_sql("fx_dashboard", conn, if_exists="append", index=False)
    
    # 2. Taxas de Bancos Centrais
    cb_data = [
        {"banco_central": "BCB - Brasil", "taxa_nome": "Selic Meta", "valor": 14.25, "data_ref": "2026-08-05"},
        {"banco_central": "FED - EUA", "taxa_nome": "Fed Funds Rate", "valor": 3.63, "data_ref": "2026-06-01"},
        {"banco_central": "BCE - Eurozona", "taxa_nome": "Deposit Facility Rate", "valor": 2.25, "data_ref": "2026-07-29"}
    ]
    df_cb = pd.DataFrame(cb_data)
    df_cb.to_sql("cb_rates", conn, if_exists="replace", index=False)
    
    # 3. Dados de Comércio Exterior (Comex)
    trade_data = [
        {"pais": "Brasil", "mes_ref": "2026-06-01", "exportacoes_usd_mi": 8830.30, "importacoes_usd_mi": 36417.30, "saldo_usd_mi": 27587.10}
    ]
    df_trade = pd.DataFrame(trade_data)
    df_trade.to_sql("trade_data", conn, if_exists="replace", index=False)
    
    conn.close()
    return f"Dados do CurrenFlux atualizados com sucesso no banco {DB_PATH}!"

# ---------------------------------------------------------
# ETAPA 2: Ferramenta de Exportação
# ---------------------------------------------------------
@tool
def export_query_to_excel(query_sql: str, file_path: str = "currenflux_report.xlsx") -> str:
    """Executa uma consulta SQL no banco CurrenFlux e exporta o resultado em Excel."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query_sql, conn)
    conn.close()
    
    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="CurrenFlux_Data", index=False)
    
    return f"Relatório exportado com sucesso para: {file_path}"

# ---------------------------------------------------------
# ETAPA 3: Inicialização do Banco e Modelos Locais Ollama
# ---------------------------------------------------------
# Inicializa primeiro a inserção de dados para criar as tabelas
fetch_and_load_currenflux_data.invoke({})

# Conecta ao SQLite
db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")

# LLM Especialista em SQL e Código
coder_llm = ChatOllama(model="qwen2.5-coder:3b", temperature=0)

# LLM Agente Revisor / Orquestrador
agent_llm = ChatOllama(model="gemma4:e4b", temperature=0)

# SQL Toolkit utilizando o Qwen 2.5-Coder
sql_toolkit = SQLDatabaseToolkit(db=db, llm=coder_llm)
tools = sql_toolkit.get_tools() + [fetch_and_load_currenflux_data, export_query_to_excel]

# Prompt Principal do Agente
prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "Você é o assistente oficial do projeto CurrenFlux especialista em análise macroeconômica. "
        "Você tem acesso a um banco SQLite com tabelas de câmbio (fx_dashboard), taxas de juros (cb_rates) "
        "e dados comerciais (trade_data). Use as ferramentas para responder dúvidas e gerar planilhas Excel."
    )),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Construção do Agente com Gemma 4
agent = create_openai_tools_agent(agent_llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# ---------------------------------------------------------
# ETAPA 4: Execução do Prompt de Teste
# ---------------------------------------------------------
if __name__ == "__main__":
    agent_executor.invoke({
        "input": "Compare as taxas de juros dos bancos centrais na tabela cb_rates e exporte o resultado completo para 'relatorio_juros.xlsx'."
    })