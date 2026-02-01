import logging
from dotenv import load_dotenv

load_dotenv()

from agents.common.monitoring import init as init_monitoring, capture_exceptions
from agents.common.utils import get_logger

logger = get_logger("Orchestrator")


@capture_exceptions
def run_full_pipeline():
    logger.info("Orchestrator: starting full pipeline")

    # Stocks
    try:
        logger.info("Orchestrator: running stock scout")
        from agents.stocks.scout import run as run_stock_scout
        run_stock_scout()

        logger.info("Orchestrator: running stock analyst")
        from agents.stocks.analyst import run as run_stock_analyst
        run_stock_analyst()

        logger.info("Orchestrator: running stock portfolio")
        from agents.stocks.portfolio import run as run_stock_portfolio
        run_stock_portfolio()
    except Exception as e:
        logger.exception("Error in stock pipeline: %s", e)

    # Crypto
    try:
        logger.info("Orchestrator: running crypto scout")
        from agents.crypto.scout import run as run_crypto_scout
        run_crypto_scout()

        logger.info("Orchestrator: running crypto analyst")
        from agents.crypto.analyst import run as run_crypto_analyst
        run_crypto_analyst()

        logger.info("Orchestrator: running crypto trader")
        from agents.crypto.trader import run as run_crypto_trader
        run_crypto_trader()
    except Exception as e:
        logger.exception("Error in crypto pipeline: %s", e)

    # Coach / recommender
    try:
        logger.info("Orchestrator: running coach/recommender")
        from agents.coach import run as run_coach
        run_coach()
    except Exception as e:
        logger.exception("Error in coach pipeline: %s", e)

    logger.info("Orchestrator: pipeline complete")


def main():
    init_monitoring()
    run_full_pipeline()


if __name__ == "__main__":
    main()
