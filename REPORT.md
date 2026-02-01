Summary of security and rate-limiting improvements

- Added a shared HTTP session with retries, default timeout, and User-Agent: [agents/common/http.py]
- Implemented an in-process sliding-window `RateLimiter` and `rate_limit` decorator: [agents/common/http.py]
- Reworked scraping to use the shared session and a rate-limited decorator: [agents/common/utils.py]
- Centralized DB writes behind safe wrappers (`safe_upsert`, `safe_insert`, `safe_select`) to add logging and error handling: [agents/common/db.py]
- Added a small secrets helper to centralize secret lookup and enforce required secrets: [agents/common/secrets.py]
- Added optional monitoring integrations (Sentry + Prometheus metrics) and exception capture decorator: [agents/common/monitoring.py]
- Wired monitoring initialization when running agents via `run_agents_now.py`.
- Replaced direct DB calls in agents with DB wrapper functions.
- Added unit tests for the rate limiter, secrets helper, and HTTP session: [tests/]
- Updated `requirements.txt` with monitoring and testing dependencies.

Next recommended steps:

1. Move secrets to a secure store (Vault, AWS Secrets Manager) for production.
2. Tune `@rate_limit` values per third-party provider and consider a distributed rate limiter (Redis, Cloud API Gateway) for multi-instance deployments.
3. Add CI to run the tests (`pytest`) and linting.
4. Add Sentry DSN and Prometheus scrape config in production environment.
5. Add end-to-end integration tests that mock external APIs.
