from datetime import UTC, datetime
from enum import Enum

from sqlmodel import Field, SQLModel


class EventType(Enum):
    """Типы событий в Telegram боте."""

    message = "message"
    callback = "callback"


class Event(SQLModel, table=True):
    """Событие взаимодействия с Telegram ботом."""

    id: int | None = Field(default=None, primary_key=True)
    event_type: EventType = Field(description="Тип события")
    user_id: int | None = Field(description="ID пользователя Telegram")
    username: str | None = Field(description="Имя пользователя Telegram")
    message_text: str | None = Field(description="Текст сообщения")
    callback_data: str | None = Field(description="callback_data кнопки от Telegram")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Когда произошло событие",
    )
