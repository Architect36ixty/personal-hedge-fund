import time
from agents.common.http import RateLimiter


def test_rate_limiter_allows_within_limit():
    limiter = RateLimiter(calls=3, period=1.0)
    start = time.monotonic()
    # three quick acquires should not wait
    assert limiter.acquire() == 0.0
    assert limiter.acquire() == 0.0
    assert limiter.acquire() == 0.0
    # fourth should require a wait ~<= period
    wait = limiter.acquire()
    assert wait > 0
    elapsed = time.monotonic() - start
    assert elapsed >= 0
