import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards.main_menu import (
    get_main_menu_keyboard,
    get_main_reply_keyboard,
    get_admin_reply_keyboard
)
from bot.config import ADMINS
from bot.keyboards.callbacks import UserStates
from bot.urls import URLBuilder
from data.db import get_session

logger = logging.getLogger(__name__)
start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    logger.info(
        f"User started: {message.from_user.id} "
        f"(@{message.from_user.username})"
    )
    await state.set_state(UserStates.MAIN_MENU)

    # Проверяем, является ли пользователь админом
    if message.from_user.id in ADMINS:
        await message.answer(
            text=(
                "👋 Добро пожаловать, администратор!\n\n"
                "Используйте кнопки ниже для управления ботом."
            ),
            reply_markup=await get_admin_reply_keyboard()
        )
    else:
        await message.answer(
            text=(
                "Для удобной навигации, выберите подходящую тему.\n"
                "Если не найдёшь подходящую, можешь задать вопрос, "
                "а мы поможем с ответом)"
            ),
            reply_markup=await get_main_reply_keyboard()
        )
        async with get_session() as session:
            inline_keyboard = await get_main_menu_keyboard(session)
            await message.answer(
                "Выберите тему:",
                reply_markup=inline_keyboard
            )


@start_router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    logger.info(f"Help requested: {message.from_user.id}")

    await message.answer(
        "ℹ️ Помощь\n\n"
        " /start - Главное меню\n\n"
        "Так же используйте кнопки клавиатуры для навигации по разделам."
    )


@start_router.message(lambda message: message.text == "🗒 Полезные материалы")
async def handle_useful_materials(message: Message):
    """Обработчик кнопки 'Полезные материалы'"""
    logger.info(f"Useful materials requested: {message.from_user.id}")

    text = URLBuilder.get_useful_materials_text()
    await message.answer(
        text,
        parse_mode="HTML",
        disable_web_page_preview=True
    )
