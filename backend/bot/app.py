"""Инициализация и запуск Telegram бота."""

import asyncio
from logging import getLogger
from typing import cast

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from decouple import config

from bot.handlers.admin_handlers import admin_router
from bot.handlers.callbacks import callback_router
from bot.handlers.start import start_router
from bot.middlewares.stats import InteractionEventMiddleware
from bot.middlewares.users import TrackNewUserMiddleware
from data.db import create_db_and_tables
from utils.logger import setup_logger

# Инициализация бота и диспетчера
bot = Bot(token=cast(str, config("BOT_TOKEN")))
dp = Dispatcher(storage=MemoryStorage())

setup_logger()
logger = getLogger("bot.app")


def setup_middlewares():
    """Настройка middleware для бота."""
    # Подключаем middleware для отслеживания событий
    dp.message.middleware(InteractionEventMiddleware())
    dp.callback_query.middleware(InteractionEventMiddleware())
    dp.message.middleware(TrackNewUserMiddleware())
    logger.info("Middleware подключены")


async def main():
    """Главная функция запуска бота."""

    logger.info("Starting bot...")

    # Создаем таблицы в БД (включая таблицу статистики)
    await create_db_and_tables()
    logger.info("Database tables created")

    # Настраиваем middleware
    setup_middlewares()

    # Подключаем роутеры
    dp.include_router(start_router)
    dp.include_router(callback_router)
    dp.include_router(admin_router)

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot started successfully")

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
