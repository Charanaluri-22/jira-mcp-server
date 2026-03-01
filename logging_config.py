import logging
import os


def setup_logging() -> None:
    """
    Configure process-wide logging once.
    LOG_LEVEL supports: DEBUG, INFO, WARNING, ERROR, CRITICAL.
    """
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
