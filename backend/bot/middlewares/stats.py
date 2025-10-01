from logging import getLogger
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.enums import UpdateType
from aiogram.types import CallbackQuery, Message, TelegramObject

from data.models import InteractionEvent
from stats.service import InteractionEventService

logger = getLogger(__name__)


class InteractionEventMiddleware(BaseMiddleware):
    """Middleware для отслеживания взаимодействий с ботом."""

    event_type_map = {
        Message: UpdateType.MESSAGE,
        CallbackQuery: UpdateType.CALLBACK_QUERY,
    }

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """
        Обработка события перед передачей основному обработчику.

        Args:
            handler: Следующий обработчик в цепочке
            event: Событие от Telegram (Message, CallbackQuery и т.д.)
            data: Дополнительные данные

        Returns:
            Результат выполнения handler
        """
        logger.info(f"Тип входящего события: {type(event).__name__}")

        event_type = self.event_type_map.get(type(event), None)
        user = getattr(event, "from_user", None)

        if event_type:
            event_obj = InteractionEvent(
                event_type=event_type,
                user_id=user.id if user else None,
                username=user.username if user else None,
                message_text=getattr(event, "text", None),
                callback_data=getattr(event, "data", None),
            )
            try:
                await InteractionEventService.save_event(event_obj)
                user_info = user.id if user else "Unknown"
                logger.debug(
                    f"Событие {event_type} сохранено " f"для пользователя {user_info}"
                )
            except Exception as e:
                logger.error(f"Ошибка при сохранении события: {e}")

        return await handler(event, data)
