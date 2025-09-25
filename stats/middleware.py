from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message

# from main import dp


class CounterMiddleware(BaseMiddleware):
    """Счетчик вызовов бота."""

    async def __call__(
        self,
        # Wrapped handler in middlewares chain
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        # Incoming event (Subclass of aiogram.types.base.TelegramObject)
        event: Message,
        # Contextual data. Will be mapped to handler arguments
        data: dict[str, Any],
    ) -> Any:
        return await handler(event, data)


# Присоединение middlewae к роутеру
# dp.message.middlewares(CounterMiddleware())
