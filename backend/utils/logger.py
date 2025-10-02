import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import cast

from decouple import config


def setup_logger():
    """Настройка логгера."""

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_level = cast(str, config("LOG_LEVEL", default="INFO")).upper()
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-6s | %(name)-20s | %(message)s ",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=(
            logging.StreamHandler(),
            RotatingFileHandler(
                log_dir / "bot.log",
                maxBytes=2_000_000,
                backupCount=5,
                encoding="utf-8",
            ),
        ),
    )
