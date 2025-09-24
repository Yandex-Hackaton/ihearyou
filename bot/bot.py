import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
import sys
from pathlib import Path
from dotenv import load_dotenv
import os
sys.path.append(str(Path(__file__).parent.parent))

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()


@dp.message()
async def echo_message(message: Message):    
    await message.answer(f"Вы написали: {message.text}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
