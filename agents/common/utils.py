import time
import logging
from typing import Callable, Any, List
import requests
from bs4 import BeautifulSoup

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

def rate_limit(calls: int, period: int = 60):
    """
    Decorator to limit function calls.
    Simple implementation: sleeps if called too frequently? 
    Actually, for this simple project, we might just need a sleep function.
    """
    def decorator(func):
        # This is a placeholder for a more complex decorator if needed.
        # For now, we will rely on explicit batching and sleeps in the agents.
        return func
    return decorator

def batch_process(items: List[Any], batch_size: int, process_func: Callable[[List[Any]], None], delay: float = 1.0):
    """
    Process items in batches with a delay between batches.
    """
    total = len(items)
    for i in range(0, total, batch_size):
        batch = items[i:i + batch_size]
        process_func(batch)
        if i + batch_size < total:
            time.sleep(delay)

def scrape_stock_data(symbol):
    """
    Scrape stock data from a public website as a fallback when API requests are exhausted.
    """
    url = f"https://finance.yahoo.com/quote/{symbol}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Example: Scrape the current price
        price_tag = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
        price = float(price_tag.text) if price_tag else None

        # Example: Scrape the RSI (if available on the page)
        rsi_tag = soup.find('span', text='RSI')
        rsi = float(rsi_tag.find_next('span').text) if rsi_tag else None

        return {"symbol": symbol, "price": price, "RSI": rsi}
    except Exception as e:
        print(f"Error scraping data for {symbol}: {e}")
        return None
