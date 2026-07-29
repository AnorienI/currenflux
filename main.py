import logging
from modules import fetch_fx, fetch_cb_rates, fetch_trade

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_pipeline():
    logging.info("Starting CurrenFlux Data Pipeline...")
    
    # 1. Atualizar Câmbio
    try:
        fetch_fx.run()
        logging.info("FX Data updated successfully.")
    except Exception as e:
        logging.error(f"Error updating FX Data: {e}")

    # 2. Atualizar Bancos Centrais
    try:
        fetch_cb_rates.run()
        logging.info("Central Bank rates updated successfully.")
    except Exception as e:
        logging.error(f"Error updating Central Bank rates: {e}")

    # 3. Atualizar Comércio Exterior
    try:
        fetch_trade.run()
        logging.info("Trade Data updated successfully.")
    except Exception as e:
        logging.error(f"Error updating Trade Data: {e}")

if __name__ == "__main__":
    run_pipeline()