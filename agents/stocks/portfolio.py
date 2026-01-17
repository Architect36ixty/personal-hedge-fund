from agents.common.db import get_supabase_client
from agents.common.utils import get_logger

logger = get_logger("StockPM")

INITIAL_CASH = 10000.0

def get_portfolio_state(supabase):
    # Fetch CASH balance
    response = supabase.table("portfolio_ledger").select("*").eq("asset_type", "CASH").execute()
    if not response.data:
        # Initialize if empty
        logger.info("Initializing Portfolio with $10,000 Cash")
        supabase.table("portfolio_ledger").insert({
            "asset_type": "CASH",
            "quantity": INITIAL_CASH,
            "current_value": INITIAL_CASH
        }).execute()
        return INITIAL_CASH, []
    
    cash = float(response.data[0]['current_value'])
    
    # Fetch Holdings
    holdings_resp = supabase.table("portfolio_ledger").select("*").eq("asset_type", "STOCK").execute()
    holdings = {h['symbol']: h for h in holdings_resp.data}
    
    return cash, holdings

def execute_trades():
    supabase = get_supabase_client()
    
    # 1. Get latest signals (generated today)
    # For sim, just get unchecked signals? Or just get last 24h.
    # We need a way to mark signals as 'processed' or just process latest batch.
    # Assuming run sequence: Scout -> Analyst -> PM.
    # We fetch signals created in the last hour.
    
    # Since we can't easily do complex time math in query builder without logic,
    # let's just fetch all signals ordered by time desc limit 20 and filter in python.
    
    signals_resp = supabase.table("signals").select("*").order("generated_at", desc=True).limit(20).execute()
    if not signals_resp.data:
        logger.info("No signals to process.")
        return

    # Filter to very recent signals (TODO: Implement proper 'processed' flag in DB or check timestamp)
    signals = signals_resp.data 
    
    cash, holdings = get_portfolio_state(supabase)
    
    for signal in signals:
        symbol = signal['symbol']
        action = signal['signal_type']
        confidence = float(signal['confidence'])
        
        # Simple simulation logic
        # If BUY and we have cash -> Buy $1000 worth (or confidence weighted)
        # If SELL and we have stock -> Sell all
        
        position = holdings.get(symbol)
        
        if action == "BUY":
            if confidence > 0.5 and cash > 1000:
                # Mock Price - In real real system, fetch real-time price or use last close from DB
                # We can fetch from market_data_stocks
                price_resp = supabase.table("market_data_stocks").select("close").eq("symbol", symbol).order("date", desc=True).limit(1).execute()
                if not price_resp.data: continue
                price = float(price_resp.data[0]['close'])
                
                investment = 1000.0 # Fixed bet size
                quantity = investment / price
                
                # Update Ledger (Cash)
                new_cash = cash - investment
                supabase.table("portfolio_ledger").update({"quantity": new_cash, "current_value": new_cash}).eq("asset_type", "CASH").execute()
                
                # Update Ledger (Stock)
                if position:
                    new_qty = float(position['quantity']) + quantity
                    supabase.table("portfolio_ledger").update({
                        "quantity": new_qty, 
                        # Average price logic omitted for brevity
                    }).eq("id", position['id']).execute()
                else:
                    supabase.table("portfolio_ledger").insert({
                        "asset_type": "STOCK",
                        "symbol": symbol,
                        "quantity": quantity,
                        "current_value": investment # Initial value
                    }).execute()
                    
                # Log Trade
                supabase.table("trade_logs").insert({
                    "symbol": symbol,
                    "action": "BUY",
                    "quantity": quantity,
                    "price": price,
                    "status": "EXECUTED"
                }).execute()
                
                logger.info(f"EXECUTED BUY: {symbol} x {quantity:.2f} @ ${price:.2f}")
                cash = new_cash # Update local cash for next loop
                
        elif action == "SELL":
            if position:
                qty = float(position['quantity'])
                if qty > 0:
                     # Fetch Price
                    price_resp = supabase.table("market_data_stocks").select("close").eq("symbol", symbol).order("date", desc=True).limit(1).execute()
                    if not price_resp.data: continue
                    price = float(price_resp.data[0]['close'])
                    
                    params = qty * price
                    
                    # Update Cash
                    new_cash = cash + params
                    supabase.table("portfolio_ledger").update({"quantity": new_cash, "current_value": new_cash}).eq("asset_type", "CASH").execute()
                    
                    # Remove Position
                    supabase.table("portfolio_ledger").delete().eq("id", position['id']).execute()
                    
                    # Log Trade
                    supabase.table("trade_logs").insert({
                        "symbol": symbol,
                        "action": "SELL",
                        "quantity": qty,
                        "price": price,
                        "status": "EXECUTED"
                    }).execute()
                    
                    logger.info(f"EXECUTED SELL: {symbol} x {qty:.2f} @ ${price:.2f}")
                    cash = new_cash

def run():
    logger.info("Starting Portfolio Manager...")
    execute_trades()
    logger.info("Portfolio Manager finished.")

if __name__ == "__main__":
    run()
