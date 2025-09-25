from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from sqlalchemy.orm import Session

from core.db import SessionLocal
from stats.models import Event, EventType


class CounterMiddleware(BaseMiddleware):
    """Middleware для отслеживания вызовов бота."""

    async def __call__(
        self,
        # Wrapped handler in middlewares chain
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        # Incoming event (Subclass of aiogram.types.base.TelegramObject)
        event: TelegramObject,
        # Contextual data. Will be mapped to handler arguments
        data: dict[str, Any],
    ) -> Any:
        # Проверяем, что это сообщение
        if isinstance(event, Message):
            message = event  # Type narrowing
            # Создаем сессию базы данных
            db: Session = SessionLocal()

            try:
                # Создаем запись о событии
                event_record = Event(
                    event_type=EventType.message,
                    user_id=message.from_user.id if message.from_user else None,
                    username=message.from_user.username if message.from_user else None,
                    message_text=message.text,
                    callback_data=None,
                )

                # Сохраняем в базу данных
                db.add(event_record)
                db.commit()
                db.refresh(event_record)

            except Exception as e:
                # Логируем ошибку, но не прерываем работу бота
                print(f"Error saving event to database: {e}")
                db.rollback()
            finally:
                db.close()

        # Продолжаем выполнение обработчика
        return await handler(event, data)
