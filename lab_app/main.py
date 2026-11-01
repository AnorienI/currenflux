from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from macro_service import get_latest_macro_state
from crypto_service import fetch_crypto_lab_data

app = FastAPI(
    title="Crypto & Macro Lab Hub",
    description="Backend API unificando dados macroeconômicos do CurrenFlux e cotações da carteira de testes.",
    version="1.0.0"
)

# Habilita CORS para permitir chamadas do dashboard HTML local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/dashboard-data")
def get_dashboard_data():
    """
    Retorna o payload unificado consumido pelo dashboard frontend.
    """
    macro_payload = get_latest_macro_state()
    crypto_payload = fetch_crypto_lab_data()
    
    return {
        "status": "success",
        "macro": macro_payload,
        "crypto": crypto_payload
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)