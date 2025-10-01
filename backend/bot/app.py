"""Инициализация и запуск Telegram бота."""
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from decouple import config

from .handlers.start import start_router
from .handlers.callbacks import callback_router
from .middlewares.stats import InteractionEventMiddleware
from data.db import create_db_and_tables
from utils.logger import logger

# Инициализация бота и диспетчера
bot = Bot(token=config('BOT_TOKEN'))
dp = Dispatcher(storage=MemoryStorage())


def setup_middlewares():
    """Настройка middleware для бота."""
    # Подключаем middleware для отслеживания событий
    dp.message.middleware(InteractionEventMiddleware())
    dp.callback_query.middleware(InteractionEventMiddleware())
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

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot started successfully")

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

