from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keybords.main_menu import get_main_menu_keyboard
from keybords.callbacks import UserStates
from data.db import get_session
from utils.logger import logger

start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    logger.info(f"User started: {message.from_user.id} (@{message.from_user.username})")

    await state.set_state(UserStates.MAIN_MENU)

    # Получаем клавиатуру из базы данных
    async with get_session() as session:
        keyboard = await get_main_menu_keyboard(session)
        await message.answer(
            "👋 Добро пожаловать!\n\n"
            "Этот бот поможет вам найти информацию о нарушениях слуха.\n"
            "Выберите интересующую вас категорию:",
            reply_markup=keyboard
        )


@start_router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    logger.info(f"Help requested: {message.from_user.id}")

    await message.answer(
        "ℹ️ Помощь\n\n"
        "• /start - Главное меню\n"
        "• /help - Показать это сообщение\n\n"
        "Используйте кнопки для навигации по разделам."
    )
