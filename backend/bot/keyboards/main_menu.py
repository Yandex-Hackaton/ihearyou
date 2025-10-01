from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from data.models import Content, Category
from .callbacks import (
    ButtonCallback,
    GoToMainMenuCallback,
    CategoryCallback
)


async def add_back_to_main_menu_button(builder: InlineKeyboardBuilder) -> None:
    """
    Добавляет в клавиатуру кнопку "Назад к главному меню".
    """
    builder.button(
        text="🔙 Назад к главному меню",
        callback_data=GoToMainMenuCallback().pack()
    )


async def get_main_menu_keyboard(
        session: AsyncSession) -> InlineKeyboardMarkup:
    """
    Создает главное меню с двумя основными категориями из БД.
    """
    builder = InlineKeyboardBuilder()
    query = select(Category)
    result = await session.execute(query)
    categories = result.scalars().all()
    for category in categories:
        builder.button(
            text=category.title,
            callback_data=CategoryCallback(category_id=category.id).pack()
        )
    builder.adjust(1)
    return builder.as_markup()


async def get_category_buttons_keyboard(
        category_id: int,
        session: AsyncSession) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками для конкретной категории.
    """
    builder = InlineKeyboardBuilder()
    try:
        query = select(Content).where(Content.category_id == category_id)
        result = await session.execute(query)
        buttons = result.scalars().all()

        for button in buttons:
            builder.button(
                text=button.title,
                callback_data=ButtonCallback(button_id=button.id).pack()
            )

        builder.button(
            text="🔙 Назад к главному меню",
            callback_data=GoToMainMenuCallback().pack()
        )
        builder.adjust(1)

    except Exception:
        builder.button(
            text="❌ Ошибка загрузки данных",
            callback_data=GoToMainMenuCallback().pack()
        )
        builder.adjust(1)

    return builder.as_markup()

