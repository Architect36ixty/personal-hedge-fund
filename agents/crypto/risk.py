from agents.common.utils import get_logger

logger = get_logger("RiskManager")

MAX_POSITION_SIZE_ZAR = 500.0 

def check_risk(signal, current_holdings, current_price):
    action = signal['signal_type']
    confidence = float(signal['confidence'])
    
    logger.info(f"Evaluating Risk for {action} signal...")
    
    if action == "BUY":
        trade_size = MAX_POSITION_SIZE_ZAR * confidence
        logger.info(f"Approved BUY size: {trade_size:.2f} ZAR")
        return True, trade_size
        
    elif action == "SELL":
        return True, 0

    return False, 0
