import pandas as pd
from agents.common.db import get_supabase_client
from agents.common.utils import get_logger

logger = get_logger("TheCoach")

def fetch_trade_history(days=7):
    supabase = get_supabase_client()
    # Fetch trades from the last X days
    # (In a real scenario, we'd filter by timestamp > now - 7 days. 
    # For now, just fetching last 100 trades to keep it simple)
    try:
        response = supabase.table("trade_logs").select("*").order("timestamp", desc=True).limit(100).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error fetching trade logs: {e}")
        return []

def get_current_config(key):
    supabase = get_supabase_client()
    try:
        resp = supabase.table("system_config").select("value").eq("key", key).execute()
        if resp.data:
            return float(resp.data[0]['value'])
    except Exception as e:
        logger.error(f"Error fetching config {key}: {e}")
    return None

def update_config(key, new_value, reason):
    supabase = get_supabase_client()
    try:
        # Update config
        supabase.table("system_config").update({"value": new_value, "updated_at": "now()"}).eq("key", key).execute()
        
        # Log action
        supabase.table("system_logs").insert({
            "event_type": "PARAM_UPDATE",
            "details": f"Updated {key} to {new_value}. Reason: {reason}"
        }).execute()
        
        logger.info(f"Updated {key} -> {new_value} ({reason})")
    except Exception as e:
        logger.error(f"Error updating config: {e}")

def run():
    logger.info("Starting The Coach (Optimization Loop)...")
    
    trades = fetch_trade_history()
    if not trades:
        logger.info("No trades found to analyze. Exiting.")
        return

    df = pd.DataFrame(trades)
    
    # 1. Calculate Win Rate (Simple logic: If we sold, did we sell higher than buy? 
    # This requires matching buy/sell orders which is complex without a sophisticated ledger.
    # For this prototype, let's assume 'Profitability' based on 'trade_logs' is hard to derive 
    # perfectly without matching. 
    # PROXY METRIC: Let's assume user manually inputs 'Win' or we sim it.
    # actually, let's just look at the 'Crypto' trades since they are simpler 'Simulated Executed'.
    # If we don't have PnL data, we can't optimize.
    # RETROACTIVE FIX: We need to know if trades were profitable.
    # Since we lack real execution data, let's use a PLACEHOLDER optimization strategy:
    # "If number of trades < 5, loosen parameters (make it easier to trade)."
    # "If number of trades > 20, tighten parameters (be more selective)."
    
    trade_count = len(df)
    logger.info(f"Analyzed {trade_count} recent trades.")
    
    # Dynamic Tuning Logic
    
    # -- TUNING: RSI (Stocks) --
    rsi_threshold = get_current_config("rsi_buy_threshold") or 30
    if trade_count < 5:
        # Not enough action? Loosen RSI (e.g. 30 -> 35)
        new_rsi = min(rsi_threshold + 2, 45) # Max cap 45
        if new_rsi != rsi_threshold:
            update_config("rsi_buy_threshold", new_rsi, "Low trade volume - loosening constraints")
            
    elif trade_count > 20:
        # Too much action? Tighten RSI
        new_rsi = max(rsi_threshold - 2, 20)
        if new_rsi != rsi_threshold:
            update_config("rsi_buy_threshold", new_rsi, "High trade volume - tightening constraints")

    # -- TUNING: Crypto Position Size --
    # In a real app, we'd check PnL. If PnL > 0, increase size.
    # Here, we'll randomize or increment slightly to demonstrate the loop.
    max_pos = get_current_config("crypto_max_pos_size") or 500
    if max_pos < 1000:
        # "Optimism bias" - slowly scale up
        update_config("crypto_max_pos_size", max_pos + 50, "Weekly scaling up")

    logger.info("Coach finished optimization.")

def insert_mock_trades():
    """
    Insert mock trades into the trade_logs table for testing.
    """
    supabase = get_supabase_client()
    mock_trades = [
        {"symbol": "AAPL", "trade_type": "BUY", "price": 150, "quantity": 10, "timestamp": "2026-01-18T10:00:00Z"},
        {"symbol": "TSLA", "trade_type": "SELL", "price": 700, "quantity": 5, "timestamp": "2026-01-18T11:00:00Z"},
    ]
    try:
        supabase.table("trade_logs").insert(mock_trades).execute()
        logger.info("Inserted mock trades for testing.")
    except Exception as e:
        logger.error(f"Error inserting mock trades: {e}")

# Call the function to insert mock trades
insert_mock_trades()

if __name__ == "__main__":
    run()
