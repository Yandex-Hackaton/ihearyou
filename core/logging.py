import logging

from core.config import config


def setup_logging() -> None:
    logging.basicConfig(level=logging.INFO if config.debug else logging.WARNING)
