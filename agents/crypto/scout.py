import requests
import time
import os
from agents.common.db import get_supabase_client
from agents.common.utils import get_logger, batch_process
from bs4 import BeautifulSoup

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

def scrape_weather_data():
    """
    Scrape weather data from a public weather website as a fallback.
    """
    url = f"https://www.timeanddate.com/weather/south-africa/johannesburg"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract temperature
        temp_tag = soup.find('div', class_='h2')
        temperature = float(temp_tag.text.strip().replace('°C', '')) if temp_tag else None

        # Extract weather condition
        condition_tag = soup.find('p', class_='bk-focus__qlook')
        condition = condition_tag.text.strip() if condition_tag else None

        return {"temperature": temperature, "condition": condition}
    except Exception as e:
        logger.error(f"Error scraping weather data: {e}")
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
        return score
    except Exception as e:
        logger.warning(f"Weather API failed, falling back to scraping: {e}")
        scraped_data = scrape_weather_data()
        if scraped_data:
            logger.info(f"Scraped Weather Data: {scraped_data}")
            # Normalize scraped data to a score
            condition = scraped_data.get("condition", "").lower()
            if "clear" in condition:
                return 90
            elif "cloud" in condition:
                return 60
            elif "rain" in condition:
                return 30
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
