from agents.common.db import get_supabase_client
from agents.common.utils import get_logger

logger = get_logger("CryptoAnalyst")

def run():
    logger.info("Starting Crypto Analyst...")
    supabase = get_supabase_client()
    
    # Fetch latest crypto data
    try:
        resp = supabase.table("market_data_crypto").select("*").eq("symbol", "XBTZAR").order("date", desc=True).limit(1).execute()
        if not resp.data:
            logger.info("No data found.")
            return
            
        data = resp.data[0]
        weather_score = float(data['weather_score'] or 50)
        
        # Fetch Dynamic Config
        try:
            cfg_resp = supabase.table("system_config").select("value").eq("key", "weather_buy_threshold").execute()
            buy_thresh = float(cfg_resp.data[0]['value']) if cfg_resp.data else 80
        except:
            buy_thresh = 80

        # Strategy
        signal_type = "HOLD"
        confidence = 0.5
        
        if weather_score > buy_thresh:
            signal_type = "BUY"
            confidence = 0.7
        elif weather_score < 30:
            signal_type = "SELL"
            confidence = 0.6
            
        if signal_type != "HOLD":
            supabase.table("signals").insert({
                "symbol": "XBTZAR",
                "signal_type": signal_type,
                "confidence": confidence,
                "agent_id": "analyst_crypto"
            }).execute()
            logger.info(f"Generated {signal_type} signal based on Weather Score: {weather_score}")
        else:
            logger.info(f"Market Neutral. Weather Score: {weather_score}")
            
    except Exception as e:
        logger.error(f"Error in Analyst: {e}")

if __name__ == "__main__":
    run()
