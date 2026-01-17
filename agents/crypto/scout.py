import requests
import time
import os
from agents.common.db import get_supabase_client
from agents.common.utils import get_logger

logger = get_logger("CryptoScout")

# Monitoring major user base location or random financial hub for "weather sentiment"
CITY_LAT = "-26.2041" # Johannesburg
CITY_LON = "28.0473"

def fetch_luno_ticker(pair="XBTZAR"):
    """
    Fetch Ticker from Luno (Public API).
    """
    url = f"https://api.luno.com/api/1/ticker?pair={pair}"
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.error(f"Luno API Error: {e}")
        return None

def fetch_weather_score():
    """
    Fetch current weather and normalize to a 'mood' score (0-100).
    """
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        logger.warning("OPENWEATHER_API_KEY not set.")
        return 50 # Neutral default

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={CITY_LAT}&lon={CITY_LON}&appid={api_key}&units=metric"
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        
        weather_id = data['weather'][0]['id']
        
        score = 50
        if weather_id == 800: # Clear
            score = 90
        elif 800 < weather_id < 900: # Clouds
            score = 60
        elif weather_id < 600: # Rain
            score = 30
        
        # Temp modifier
        temp = data['main']['temp']
        if 20 <= temp <= 25:
            score += 10
            
        return min(max(score, 0), 100)
    except Exception as e:
        logger.error(f"Weather API Error: {e}")
        return 50

def run():
    logger.info("Starting Crypto Scout...")
    supabase = get_supabase_client()
    
    # 1. Fetch Price
    pair = "XBTZAR" # Bitcoin / South African Rand
    ticker_data = fetch_luno_ticker(pair)
    
    if not ticker_data:
        return

    # 2. Fetch Weather
    weather_score = fetch_weather_score()
    
    # 3. Store
    try:
        record = {
            "symbol": pair,
            "date": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(int(ticker_data['timestamp'])/1000)),
            "close": float(ticker_data['last_trade']),
            "volume": float(ticker_data['rolling_24_hour_volume']),
            "weather_score": weather_score
        }
        
        supabase.table("market_data_crypto").upsert(record, on_conflict="symbol,date").execute()
        logger.info(f"Stored Crypto Data: {record['close']} ZAR | Weather: {weather_score}")
        
    except Exception as e:
        logger.error(f"Supabase upsert error: {e}")

if __name__ == "__main__":
    run()
