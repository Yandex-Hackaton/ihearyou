from datetime import datetime

from aiogram.enums import UpdateType
from sqlmodel import Field, SQLModel


class InteractionEvent(SQLModel, table=True):
    """Событие взаимодействия с Telegram ботом."""

    id: int | None = Field(default=None, primary_key=True)
    event_type: UpdateType = Field(description="Тип события")
    user_id: int | None = Field(description="ID пользователя Telegram")
    username: str | None = Field(description="Имя пользователя Telegram")
    message_text: str | None = Field(description="Текст сообщения")
    callback_data: str | None = Field(description="callback_data кнопки от Telegram")
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Когда произошло событие",
    )
