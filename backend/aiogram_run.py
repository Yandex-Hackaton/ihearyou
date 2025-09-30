import asyncio
from create_bot import bot, dp
from handlers.start import start_router
from handlers.callbacks import callback_router
# from work_time.time_func import send_time_msg

async def main():
    # Подключаем роутеры
    dp.include_router(start_router)
    dp.include_router(callback_router)
    
    # scheduler.add_job(send_time_msg, 'interval', seconds=10)
    # scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())