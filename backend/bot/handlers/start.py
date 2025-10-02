import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from data.db import get_session

from ..keyboards.callbacks import UserStates
from ..keyboards.main_menu import get_main_menu_keyboard, get_main_reply_keyboard

logger = logging.getLogger(__name__)
start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    logger.info(
        f"User started: {message.from_user.id} " f"(@{message.from_user.username})"
    )
    await state.set_state(UserStates.MAIN_MENU)
    await message.answer(
        text=(
            "👋 Добро пожаловать!\n\n"
            "Этот бот поможет вам найти информацию о нарушениях слуха.\n"
        ),
        reply_markup=await get_main_reply_keyboard()
    )
    async with get_session() as session:
        inline_keyboard = await get_main_menu_keyboard(session)
        await message.answer(
            "Выберите интересующую вас категорию:",
            reply_markup=inline_keyboard
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
