import os
import logging
from typing import Callable

try:
    import sentry_sdk
except Exception:
    sentry_sdk = None

try:
    from prometheus_client import Counter, start_http_server
except Exception:
    Counter = None
    start_http_server = None

logger = logging.getLogger("monitoring")

# Prometheus metrics (optional)
external_requests_total = None
external_requests_failures = None


def init(prometheus_port: int = 8000):
    """Initialize optional monitoring integrations: Sentry and Prometheus.

    Both are enabled only if the related packages are installed and env vars provided.
    """
    # Sentry
    dsn = os.environ.get("SENTRY_DSN")
    if dsn and sentry_sdk:
        try:
            sentry_sdk.init(dsn)
            logger.info("Sentry initialized")
        except Exception as e:
            logger.exception("Failed to initialize Sentry: %s", e)
    elif dsn:
        logger.warning("SENTRY_DSN provided but sentry-sdk not installed")

    # Prometheus
    global external_requests_total, external_requests_failures
    if Counter is not None:
        external_requests_total = Counter("phf_external_requests_total", "Total external HTTP requests")
        external_requests_failures = Counter("phf_external_requests_failures", "External request failures")
        if start_http_server:
            try:
                start_http_server(prometheus_port)
                logger.info("Prometheus metrics server started on port %d", prometheus_port)
            except Exception as e:
                logger.exception("Could not start Prometheus server: %s", e)
    else:
        logger.debug("prometheus_client not available; skipping metrics setup")


def incr_request(success: bool = True):
    if external_requests_total:
        external_requests_total.inc()
    if not success and external_requests_failures:
        external_requests_failures.inc()


def capture_exceptions(func: Callable):
    """Decorator that sends exceptions to Sentry (if configured) and re-raises."""
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if sentry_sdk:
                try:
                    sentry_sdk.capture_exception(e)
                except Exception:
                    logger.exception("Failed to report exception to Sentry")
            raise
    return wrapped
