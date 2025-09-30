from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from data.models import Role, Category, Button


async def get_category_by_id(category_id: int, session: AsyncSession) -> Optional[Category]:
    query = select(Category).where(Category.id == category_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_button_by_id(button_id: int, session: AsyncSession) -> Optional[Button]:
    query = select(Button).where(Button.id == button_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_menu_buttons_title(user_role_slug: str,
                                 session: AsyncSession) -> List[str]:
    """
    Получает названия кнопок меню для конкретной роли пользователя.
    """
    query = (
        select(Button.title)
        .join(Button.category)
        .join(Category.for_user_role)
        .where(Role.slug == user_role_slug)
    )
    result = await session.execute(query)
    return result.scalars().all()


async def get_content_for_button(button_title: str,
                                 session: AsyncSession) -> str:
    """
    Получает контент для конкретной кнопки по ее названию.
    """
    query = select(Button.content).where(Button.title == button_title)
    result = await session.execute(query)
    content = result.scalar_one_or_none()
    return content if content else (
        "Извините, для этого пункта пока нет информации."
    )
