from datetime import datetime, timedelta
from typing import Optional

from aiogram.enums import UpdateType
from sqlalchemy import BigInteger, Column, DateTime, Integer, String, Text, ForeignKey
from sqlmodel import Field, Relationship, SQLModel

from enums.fields import InitValue, Length, ViewLimits
from enums.msg import AnswerChoices

from .mixins import BaseCreatedAtFieldMixin, BaseIDMixin, BaseInfoMixin


class Category(
    BaseIDMixin,
    BaseInfoMixin,
    BaseCreatedAtFieldMixin,
    table=True,
):
    __tablename__ = 'categories'

    is_active: bool

    contents: list['Content'] = Relationship(back_populates='category')

    def __str__(self) -> str:
        return self.title


class Content(
    BaseIDMixin,
    BaseInfoMixin,
    BaseCreatedAtFieldMixin,
    table=True,
):
    __tablename__ = 'contents'

    url_link: Optional[str] = Field(
        sa_column=String(Length.URL_LINK_FIELD.value),
    )
    image_url: Optional[str] = Field(
        sa_column=String(Length.URL_LINK_FIELD.value),
    )
    file_id: Optional[str] = Field(
        sa_column=String(255),
    )
    is_active: bool
    views_count: int = Field(
        default=InitValue.DEFAULT_START_VALUE.value,
        sa_column=Column(
            Integer,
            nullable=False,
            server_default=str(InitValue.DEFAULT_START_VALUE.value),
        ),
    )

    category_id: int = Field(foreign_key=f'{Category.__tablename__}.id')
    category: Category = Relationship(back_populates='contents')

    ratings: list['Rating'] = Relationship(back_populates='content')


class User(SQLModel, table=True):
    __tablename__ = 'users'

    telegram_id: Optional[int] = Field(
        sa_column=Column(BigInteger, primary_key=True, autoincrement=False),
    )
    username: Optional[str] = Field(unique=True, index=True)
    password: Optional[str] = Field(
        default=None,
        sa_column=String(Length.PASSWORD_FIELD.value),
    )
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    registered_at: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(hours=3),
        sa_type=DateTime(timezone=True),
    )

    questions: list['Question'] = Relationship(back_populates='user')
    ratings: list['Rating'] = Relationship(back_populates='user')

    def __str__(self) -> str:
        return self.username or f'User {self.telegram_id}'


class Question(BaseIDMixin, BaseCreatedAtFieldMixin, table=True):
    __tablename__ = 'questions'

    text: Optional[str] = Field(sa_type=Text())
    answer_text: Optional[str] = Field(sa_type=Text())

    user_id: int = Field(
        sa_column=Column(
            BigInteger, 
            ForeignKey('users.telegram_id'), 
            nullable=False
        )
    )
    user: User = Relationship(back_populates='questions')

    def __str__(self) -> str:
        return (
            f'Question #{self.id}: '
            f'{self.text[:ViewLimits.TEXT_FIELD.value]}'
            f'{'...' if len(self.text) > ViewLimits.TEXT_FIELD.value else ''}'
        )


class InteractionEvent(
    BaseIDMixin,
    BaseCreatedAtFieldMixin,
    table=True,
):
    '''Событие взаимодействия с Telegram ботом.'''

    __tablename__ = 'interaction_events'

    event_type: UpdateType
    user_id: int = Field(sa_column=Column(BigInteger, nullable=False))
    message_text: Optional[str]
    callback_data: Optional[str]

    def __str__(self) -> str:
        return f"Event #{self.id}: {self.event_type}"


class Rating(
    BaseIDMixin,
    BaseCreatedAtFieldMixin,
    table=True,
):
    '''Рейтинг контента от пользователя.'''

    __tablename__ = 'ratings'

    is_helpful: Optional[bool]
    score: Optional[int] = Field(default=None)

    user_id: int = Field(
        sa_column=Column(
            BigInteger, 
            ForeignKey('users.telegram_id'), 
            nullable=False
        )
    )
    user: User = Relationship(back_populates='ratings')

    content_id: int = Field(foreign_key=f'{Content.__tablename__}.id')
    content: Content = Relationship(back_populates='ratings')

    def __str__(self) -> str:
        status_map = {
            True: AnswerChoices.HELPFUL.value,
            False: AnswerChoices.NOT_HELPFUL.value,
            None: AnswerChoices.NO_RATING.value,
        }
        return (
            f'Rating #{self.id}: {status_map.get(self.is_helpful)} '
            f'by User {self.user_id}'
        )
