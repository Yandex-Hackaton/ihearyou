from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, BigInteger, DateTime, func
from passlib.context import CryptContext

from .mixins import BaseInfoMixin


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Category(BaseInfoMixin, SQLModel, table=True):
    __tablename__ = 'categories'

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    is_active: bool

    contents: list['Content'] = Relationship(
        back_populates='category',
        sa_relationship_kwargs={'lazy': 'selectin'},
    )


class Content(BaseInfoMixin, SQLModel, table=True):
    __tablename__ = 'contents'

    text: Optional[str]
    image_path: Optional[str]  # реализовать хранение файла изображения
    url_link: Optional[str]
    is_active: bool
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    category_id: int = Field(foreign_key=f'{Category.__tablename__}.id')
    category: Category = Relationship(
        back_populates='contents',
        sa_relationship_kwargs={'lazy': 'selectin'},
    )


class User(SQLModel, table=True):
    __tablename__ = 'users'

    telegram_id: int = Field(
        sa_column=Column(BigInteger, primary_key=True, autoincrement=False),
    )
    username: Optional[str] = Field(unique=True, index=True)
    password: Optional[str]
    is_blocked: bool
    is_admin: bool
    registered_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    questions: list['Question'] = Relationship(
        back_populates='user',
        sa_relationship_kwargs={'lazy': 'selectin'},
    )


class Question(SQLModel, table=True):
    __tablename__ = 'questions'

    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    user_id: int = Field(foreign_key=f'{User.__tablename__}.telegram_id')
    user: User = Relationship(
        back_populates='questions',
        sa_relationship_kwargs={'lazy': 'selectin'},
    )
