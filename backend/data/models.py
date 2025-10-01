from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Integer, BigInteger, DateTime, text
from aiogram.enums import UpdateType

from .mixins import BaseInfoMixin


class Category(BaseInfoMixin, SQLModel, table=True):
    __tablename__ = 'categories'

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=text("NOW() + INTERVAL '3 hours'")),
    )
    is_active: bool

    contents: list['Content'] = Relationship(back_populates='category')

    def __str__(self) -> str:
        return self.title


class Content(BaseInfoMixin, SQLModel, table=True):
    __tablename__ = 'contents'

    id: Optional[int] = Field(default=None, primary_key=True)
    url_link: Optional[str]
    is_active: bool
    views_count: int = Field(
        default=0,
        sa_column=Column(Integer, nullable=False, server_default="0"),
        description='Количество просмотров контента',
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=text("NOW() + INTERVAL '3 hours'")),
    )
    category_id: int = Field(foreign_key=f'{Category.__tablename__}.id')
    category: Category = Relationship(back_populates='contents')

    def __str__(self) -> str:
        return self.title


class User(SQLModel, table=True):
    __tablename__ = 'users'

    telegram_id: Optional[int] = Field(
        sa_column=Column(BigInteger, primary_key=True, autoincrement=False),
    )
    username: Optional[str] = Field(unique=True, index=True)
    password: Optional[str]
    is_active: bool
    is_admin: bool
    registered_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=text("NOW() + INTERVAL '3 hours'"))
    )

    questions: list['Question'] = Relationship(back_populates='user')

    def __str__(self) -> str:
        return self.username or f"User {self.telegram_id}"


class Question(SQLModel, table=True):
    __tablename__ = 'questions'

    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=text("NOW() + INTERVAL '3 hours'")),
    )
    answer: Optional[str]

    user_id: int = Field(foreign_key=f'{User.__tablename__}.telegram_id')
    user: User = Relationship(
        back_populates='questions')

    def __str__(self) -> str:
        return f"Question #{self.id}: {self.text[:50]}{'...' if len(self.text) > 50 else ''}"


class InteractionEvent(SQLModel, table=True):
    """Событие взаимодействия с Telegram ботом."""

    __tablename__ = 'interaction_events'

    id: Optional[int] = Field(default=None, primary_key=True)
    event_type: UpdateType = Field(description="Тип события")
    user_id: Optional[int] = Field(
        description="ID пользователя Telegram"
    )
    username: Optional[str] = Field(
        description="Имя пользователя Telegram"
    )
    message_text: Optional[str] = Field(description="Текст сообщения")
    callback_data: Optional[str] = Field(
        description="callback_data кнопки от Telegram"
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("NOW() + INTERVAL '3 hours'")
        ),
        description="Когда произошло событие",
    )

    def __str__(self) -> str:
        username_or_id = self.username or self.user_id
        return f"Event #{self.id}: {self.event_type} from {username_or_id}"
