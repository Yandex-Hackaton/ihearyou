from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

start_router = Router()

@start_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Запуск сообщения по команде /start используя фильтр CommandStart()')