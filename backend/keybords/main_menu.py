from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from data.models import Button, Category, Role
from .callbacks import MainMenuCallback, ButtonCallback


async def get_main_menu_keyboard(session: AsyncSession) -> InlineKeyboardMarkup:
    """
    Создает главное меню с двумя основными категориями из БД
    """
    builder = InlineKeyboardBuilder()
    
    # Get all categories from database
    query = select(Category).join(Role)
    result = await session.execute(query)
    categories = result.scalars().all()
    
    # Create buttons for each category
    for category in categories:
        builder.button(
            text=category.title,
            callback_data=MainMenuCallback(category_id=category.id).pack()
        )
    
    # Configure layout (2 buttons per row)
    builder.adjust(1)
    
    return builder.as_markup()


async def get_category_buttons_keyboard(category_id: int, session: AsyncSession) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками для конкретной категории
    """
    builder = InlineKeyboardBuilder()
    
    try:
        # Get all buttons for the specific category using explicit query
        query = select(Button).where(Button.category_id == category_id)
        result = await session.execute(query)
        buttons = result.scalars().all()
        
        if not buttons:
            builder.button(
                text="❌ Нет доступных разделов",
                callback_data=MainMenuCallback(category_id=0).pack()
            )
        else:
            # Create buttons for each subcategory
            for button in buttons:
                builder.button(
                    text=button.title,
                    callback_data=ButtonCallback(button_id=button.id).pack()
                )
        
        # Add button "Back to main menu"
        builder.button(
            text="🔙 Назад к главному меню",
            callback_data=MainMenuCallback(category_id=0).pack()
        )
        
        # Configure layout (1 button per row)
        builder.adjust(1)
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке кнопок категории: {e}")
        builder.button(
            text="❌ Ошибка загрузки данных",
            callback_data=MainMenuCallback(category_id=0).pack()
        )
        builder.adjust(1)
    
    return builder.as_markup()