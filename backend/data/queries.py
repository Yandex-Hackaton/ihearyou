from logging import getLogger
from typing import Optional

from aiogram.types import User as TG_User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from data.models import Category, Content, User

logger = getLogger(__name__)


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


async def get_or_create_user(tg_user: TG_User, session: AsyncSession) -> User:
    """Получить объект пользоватетя или создать новый.
    Так же обновляет username, если он изменился.

    Args:
        tg_user: это объект User от aiogram, например `message.from_user`
    """
    user = await session.get(User, tg_user.id)
    if user:
        if user.username != tg_user.username:
            logger.info(f"User {user.telegram_id} updated username to {user.username}")
            user.username = tg_user.username
        return user
    else:
        user = User(
            telegram_id=tg_user.id,
            username=tg_user.username,
        )
        session.add(user)
        logger.info(f"New user created: {user.telegram_id=}, {user.username=}")
        return user


async def set_user_inactive(telegram_id: int, session: AsyncSession) -> None:
    """Установить пользователя как неактивного."""
    user = await session.get(User, telegram_id)
    if user:
        user.is_active = False
        logger.info(f"User {telegram_id} set to inactive")


async def set_user_active(telegram_id: int, session: AsyncSession) -> None:
    """Установить пользователя как активного."""
    user = await session.get(User, telegram_id)
    if user:
        user.is_active = True
        logger.info(f"User {telegram_id} set to active")
