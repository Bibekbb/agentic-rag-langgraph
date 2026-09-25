import logging
import sys
from app.config import settings

def setup_logging() -> None:
    logging.basicConfig(
        level = settings.LOG_LEVEL,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)