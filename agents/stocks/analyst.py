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

def analyze_and_signal(records):
    supabase = get_supabase_client()
    signals = []

    logger.info(f"Analyzing {len(records)} records...")
    
    for row in records:
        symbol = row.get('symbol')
        rsi = row.get('rsi')
        macd = row.get('macd')
        
        if rsi is None or macd is None:
            logger.warning(f"Incomplete data for {symbol}, skipping analysis.")
            continue
            
        signal_type = "HOLD"
        confidence = 0.0
        
        # Simple Strategy
        # Buy: RSI < 30 (Oversold) AND MACD > 0 (Momentum) ? Or MACD Crossover?
        # Let's keep it simple as requested: "If RSI < 30 and Sentiment > Positive" (I don't have sentiment in DB yet)
        # So I will fallback to RSI & MACD
        
        rsi = float(rsi)
        macd = float(macd)
        
        if rsi < 30:
            signal_type = "BUY"
            confidence = (30 - rsi) / 30.0 # higher confidence if deeper oversold
        elif rsi > 70:
            signal_type = "SELL"
            confidence = (rsi - 70) / 30.0
            
        # Refine with MACD
        if signal_type == "BUY" and macd < 0:
            confidence *= 0.8 # Reduce confidence if MACD is negative (downtrend)
        
        if signal_type != "HOLD":
            logger.info(f"Generated {signal_type} signal for {symbol} (Conf: {confidence:.2f})")
            signals.append({
                "symbol": symbol,
                "signal_type": signal_type,
                "confidence": round(confidence, 2),
                "agent_id": "analyst_stock",
                # "generated_at": now... (Supabase default)
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
