import pandas as pd
from agents.common.db import get_supabase_client
from agents.common.utils import get_logger

logger = get_logger("StockAnalyst")

def fetch_latest_market_data():
    supabase = get_supabase_client()
    # Fetch today's data (or strict latest)
    # Simply order by date desc limit 20 (assuming 10 stocks, maybe 15) to get latest batch
    try:
        response = supabase.table("market_data_stocks").select("*").order("date", desc=True).limit(50).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error fetching from DB: {e}")
        return []

def get_config(key, default):
    supabase = get_supabase_client()
    try:
        resp = supabase.table("system_config").select("value").eq("key", key).execute()
        if resp.data:
            return float(resp.data[0]['value'])
    except:
        pass
    return default

def analyze_and_signal(records):
    supabase = get_supabase_client()
    signals = []

    # DYNAMIC CONFIG: Fetch thresholds from DB
    rsi_buy_limit = get_config("rsi_buy_threshold", 30)
    rsi_sell_limit = get_config("rsi_sell_threshold", 70)

    logger.info(f"Analyzing {len(records)} records with RSI Buy < {rsi_buy_limit}...")
    
    for row in records:
        symbol = row.get('symbol')
        rsi = row.get('rsi')
        macd = row.get('macd')
        
        if rsi is None or macd is None:
            # logger.warning(f"Incomplete data for {symbol}") 
            continue
            
        signal_type = "HOLD"
        confidence = 0.0
        
        rsi = float(rsi)
        macd = float(macd)
        
        if rsi < rsi_buy_limit:
            signal_type = "BUY"
            # Confidence logic adjusted to new limit
            confidence = (rsi_buy_limit - rsi) / rsi_buy_limit 
        elif rsi > rsi_sell_limit:
            signal_type = "SELL"
            confidence = (rsi - rsi_sell_limit) / 30.0
            
        # Refine with MACD
        if signal_type == "BUY" and macd < 0:
            confidence *= 0.8
        
        if signal_type != "HOLD":
            logger.info(f"Generated {signal_type} signal for {symbol} (Conf: {confidence:.2f})")
            signals.append({
                "symbol": symbol,
                "signal_type": signal_type,
                "confidence": round(confidence, 2),
                "agent_id": "analyst_stock"
            })

    if signals:
        try:
             supabase.table("signals").insert(signals).execute()
             logger.info(f"Published {len(signals)} signals.")
        except Exception as e:
             logger.error(f"Error publishing signals: {e}")
    else:
        logger.info("No trading signals generated.")

def run():
    logger.info("Starting Stock Analyst...")
    data = fetch_latest_market_data()
    if data:
        analyze_and_signal(data)
    logger.info("Stock Analyst finished.")

if __name__ == "__main__":
    run()
