import asyncio
from create_bot import bot, dp
from handlers.start import start_router
from handlers.callbacks import callback_router
from utils.logger import logger


async def main():
    logger.info("Starting bot...")
    
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
