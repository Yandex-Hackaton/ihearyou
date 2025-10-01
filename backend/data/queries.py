"""Запросы к базе данных."""

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from data.models import Category, Content
from utils.logger import logger


async def get_category_by_id(
    category_id: int, session: AsyncSession
) -> Optional[Category]:
    """Получить категорию по ID."""
    query = select(Category).where(Category.id == category_id)
    result = await session.execute(query)
    category = result.scalar_one_or_none()

    if not category:
        logger.warning(f"Category not found in DB: {category_id}")

    return category


async def get_button_by_id(button_id: int, session: AsyncSession) -> Optional[Content]:
    """Получить контент (кнопку) по ID."""
    query = select(Content).where(Content.id == button_id)
    result = await session.execute(query)
    button = result.scalar_one_or_none()

    if not button:
        logger.warning(f"Button not found in DB: {button_id}")

    return button


async def get_content_for_button(button_title: str, session: AsyncSession) -> str:
    """Получить контент для конкретной кнопки по ее названию."""
    query = select(Content.content).where(Content.title == button_title)
    result = await session.execute(query)
    content = result.scalar_one_or_none()
    return content if content else ("Извините, для этого пункта пока нет информации.")
