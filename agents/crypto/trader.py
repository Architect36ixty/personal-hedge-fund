import os
import requests
from requests.auth import HTTPBasicAuth
from agents.common.db import get_supabase_client
from agents.common.utils import get_logger
import agents.crypto.risk as risk
from agents.common.http import get_session

logger = get_logger("CryptoTrader")

def get_luno_auth():
    key_id = os.environ.get("LUNO_API_KEY_ID")
    key_secret = os.environ.get("LUNO_API_KEY_SECRET")
    if not key_id or not key_secret:
        raise ValueError("Luno API Credentials missing.")
    return HTTPBasicAuth(key_id, key_secret)

def execute_luno_order(pair, type, volume=None): 
    # Placeholder for Luno API call
    logger.info(f"--- SIMULATED EXECUTION ---")
    logger.info(f"Placing {type} order for {pair}. Volume/Value: {volume}")
    return {"order_id": "sim_12345", "status": "PENDING"}

def run():
    logger.info("Starting Crypto Trader...")
    supabase = get_supabase_client()
    
    try:
        resp = supabase.table("signals").select("*").eq("agent_id", "analyst_crypto").order("generated_at", desc=True).limit(1).execute()
        if not resp.data:
            logger.info("No signals found.")
            return

        signal = resp.data[0]
        logger.info(f"Found Signal: {signal['signal_type']}")
        
        is_safe, amount = risk.check_risk(signal, {}, 0)
        
        if is_safe:
            if signal['signal_type'] == "BUY":
                res = execute_luno_order("XBTZAR", "BUY", volume=amount)
                # Log trade in DB via wrapper
                from agents.common import db as common_db

                common_db.safe_insert("trade_logs", [{
                    "symbol": "XBTZAR",
                    "action": "BUY",
                    "quantity": amount,
                    "price": 0,
                    "status": "EXECUTED_SIM"
                }])
                
            elif signal['signal_type'] == "SELL":
                res = execute_luno_order("XBTZAR", "SELL")
                from agents.common import db as common_db
                common_db.safe_insert("trade_logs", [{
                    "symbol": "XBTZAR",
                    "action": "SELL",
                    "quantity": 0,
                    "price": 0,
                    "status": "EXECUTED_SIM"
                }])
        else:
            logger.warning("Trade rejected by Risk Manager.")
            
    except Exception as e:
        logger.error(f"Trader Error: {e}")

if __name__ == "__main__":
    run()
