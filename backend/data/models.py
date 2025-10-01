from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Integer, BigInteger, DateTime, text
from aiogram.enums import UpdateType

from .mixins import BaseInfoMixin, BaseCreatedAtFieldMixin
from .constants import DEF_START_VALUE, DEF_DATETIME_VIEW_STR
from enums.msg import AnswerChoices


class Category(BaseInfoMixin, BaseCreatedAtFieldMixin, table=True):
    __tablename__ = 'categories'

    id: Optional[int] = Field(default=None, primary_key=True)
    is_active: bool

    contents: list['Content'] = Relationship(back_populates='category')

    def __str__(self) -> str:
        return self.title


class Content(BaseInfoMixin, BaseCreatedAtFieldMixin, SQLModel, table=True):
    __tablename__ = 'contents'

    id: Optional[int] = Field(default=None, primary_key=True)
    url_link: Optional[str]
    is_active: bool
    views_count: int = Field(
        default=DEF_START_VALUE,
        sa_column=Column(
            Integer,
            nullable=False,
            server_default=str(DEF_START_VALUE),
        ),
    )
    category_id: int = Field(foreign_key=f'{Category.__tablename__}.id')
    category: Category = Relationship(back_populates='contents')
    ratings: list['Rating'] = Relationship(back_populates='content')

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
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text(DEF_DATETIME_VIEW_STR),
        )
    )

    questions: list['Question'] = Relationship(back_populates='user')
    ratings: list['Rating'] = Relationship(back_populates='user')

    def __str__(self) -> str:
        return self.username or f'User {self.telegram_id}'


class Question(BaseCreatedAtFieldMixin, SQLModel, table=True):
    __tablename__ = 'questions'

    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    answer: Optional[str]

    user_id: int = Field(foreign_key=f'{User.__tablename__}.telegram_id')
    user: User = Relationship(back_populates='questions')

    def __str__(self) -> str:
        return (
            f'Question #{self.id}: {self.text[:50]}'
            f'{'...' if len(self.text) > 50 else ''}'
        )


class InteractionEvent(BaseCreatedAtFieldMixin, SQLModel, table=True):
    '''Событие взаимодействия с Telegram ботом.'''

    __tablename__ = 'interaction_events'

    id: Optional[int] = Field(default=None, primary_key=True)
    event_type: UpdateType
    user_id: Optional[int]
    username: Optional[str]
    message_text: Optional[str]
    callback_data: Optional[str]

    def __str__(self) -> str:
        username_or_id = self.username or self.user_id
        return f'Event #{self.id}: {self.event_type} from {username_or_id}'


class Rating(BaseCreatedAtFieldMixin, SQLModel, table=True):
    '''Рейтинг контента от пользователя.'''

    __tablename__ = 'ratings'

    id: Optional[int] = Field(default=None, primary_key=True)
    is_helpful: Optional[bool] 
    rating: Optional[int] = Field(default=None)

    user_id: int = Field(foreign_key=f'{User.__tablename__}.telegram_id')
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
