from agents.common.utils import get_logger
from agents.common.db import get_supabase_client

logger = get_logger("RiskManager")

# Removed hardcoded MAX_POSITION_SIZE_ZAR

def get_max_position():
    supabase = get_supabase_client()
    try:
        resp = supabase.table("system_config").select("value").eq("key", "crypto_max_pos_size").execute()
        if resp.data:
            return float(resp.data[0]['value'])
    except:
        pass
    return 500.0 # Default

def check_risk(signal, current_holdings, current_price):
    action = signal['signal_type']
    confidence = float(signal['confidence'])
    
    max_pos = get_max_position()
    
    logger.info(f"Evaluating Risk for {action} signal (Max Pos: {max_pos})...")
    
    if action == "BUY":
        trade_size = max_pos * confidence
        logger.info(f"Approved BUY size: {trade_size:.2f} ZAR")
        return True, trade_size
        
    elif action == "SELL":
        return True, 0

    return False, 0
