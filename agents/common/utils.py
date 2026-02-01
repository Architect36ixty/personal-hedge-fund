import time
import logging
from typing import Callable, Any, List, Optional
from bs4 import BeautifulSoup

from agents.common.http import get_session, rate_limit

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

# Use the shared rate_limit decorator from agents.common.http


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

@rate_limit(calls=5, period=60)
def scrape_stock_data(symbol: str, timeout: Optional[float] = 10.0):
    """
    Scrape stock data from Yahoo Finance as a fallback.
    This uses a shared session with retries and timeouts and is rate-limited to
    avoid overloading the target site.
    """
    session = get_session()
    url = f"https://finance.yahoo.com/quote/{symbol}"
    try:
        resp = session.get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        price = None
        price_tag = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'})
        if price_tag and price_tag.text:
            try:
                price = float(price_tag.text.replace(',', ''))
            except Exception:
                price = None

        rsi = None
        try:
            rsi_cell = soup.find('td', text='RSI (14)')
            if rsi_cell:
                rsi_tag = rsi_cell.find_next_sibling('td')
                if rsi_tag and rsi_tag.text:
                    rsi = float(rsi_tag.text)
        except Exception:
            rsi = None

        return {"price": price, "rsi": rsi}
    except Exception as e:
        logging.getLogger("utils").warning(f"Error scraping data for {symbol}: {e}")
        return None
