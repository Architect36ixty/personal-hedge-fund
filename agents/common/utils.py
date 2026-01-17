import time
import logging
from typing import Callable, Any, List

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
