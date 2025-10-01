import logging
import sys
from pathlib import Path
from decouple import config


def setup_logger():
    """Настройка логгера."""

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_level = config("LOG_LEVEL", default="INFO").upper()

    logger = logging.getLogger("ihearyou")
    logger.setLevel(getattr(logging, log_level))

    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler("logs/bot.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()
