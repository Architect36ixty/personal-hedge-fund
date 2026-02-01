import time
import threading
from typing import Callable
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def _build_session(timeout: float = 10.0, user_agent: str = None) -> requests.Session:
    s = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=(429, 500, 502, 503, 504))
    adapter = HTTPAdapter(max_retries=retries)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    s.headers.update({
        "User-Agent": user_agent or "personal-hedge-fund-bot/1.0 (+https://github.com)"
    })
    # store a default timeout on the session for convenience
    s.request = _wrap_request_with_timeout(s.request, timeout)
    return s


def _wrap_request_with_timeout(request_func: Callable, timeout: float):
    def wrapped(method, url, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = timeout
        return request_func(method, url, **kwargs)
    return wrapped


# Global shared session for the application
_GLOBAL_SESSION = _build_session()


def get_session() -> requests.Session:
    """Return a configured requests.Session with retries and default timeout."""
    return _GLOBAL_SESSION


class RateLimiter:
    """Simple sliding-window rate limiter for in-process use.

    Not suitable for distributed rate limiting, but fine for local scripts.
    """
    def __init__(self, calls: int, period: float):
        self.calls = calls
        self.period = period
        self.lock = threading.Lock()
        self.timestamps = []

    def acquire(self):
        with self.lock:
            now = time.monotonic()
            # drop old timestamps
            cutoff = now - self.period
            while self.timestamps and self.timestamps[0] <= cutoff:
                self.timestamps.pop(0)
            if len(self.timestamps) < self.calls:
                self.timestamps.append(now)
                return 0.0
            # need to wait until the oldest timestamp exits the window
            wait = self.timestamps[0] + self.period - now
            return wait

    def __call__(self, func=None):
        if func is None:
            raise ValueError("RateLimiter must be used as a decorator with arguments via RateLimiter(calls, period)(fn)")

        def wrapper(*args, **kwargs):
            wait = self.acquire()
            if wait > 0:
                time.sleep(wait)
            return func(*args, **kwargs)

        return wrapper


def rate_limit(calls: int, period: float = 60.0):
    """Decorator factory: limit to `calls` per `period` seconds (sliding window).

    Usage:
        @rate_limit(5, 60)
        def fetch(): ...
    """
    limiter = RateLimiter(calls, period)

    def decorator(func):
        def wrapped(*args, **kwargs):
            wait = limiter.acquire()
            if wait > 0:
                time.sleep(wait)
            return func(*args, **kwargs)
        return wrapped

    return decorator
