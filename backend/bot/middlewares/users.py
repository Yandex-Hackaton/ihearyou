from logging import getLogger
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from aiogram.types import User as TG_User

from data.db import get_session
from data.queries import get_or_create_user

logger = getLogger(__name__)


class TrackNewUserMiddleware(BaseMiddleware):
    """Отслеживание новых пользователей взаимодействующих с ботом."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: TG_User | None = getattr(event, "from_user", None)

        if user and isinstance(event, Message) and event.text == "/start":
            async with get_session() as session:
                try:
                    await get_or_create_user(user, session)
                except Exception as e:
                    logger.error(f"Error tracking new user {user.id}: {e}")

        return await handler(event, data)
