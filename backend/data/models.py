from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Integer, BigInteger, DateTime, func
from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import ImageType

from .mixins import BaseInfoMixin


storage = FileSystemStorage(path="/media")


class Category(BaseInfoMixin, SQLModel, table=True):
    __tablename__ = 'categories'

    id: Optional[int] = Field(default=None, primary_key=True)
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

    id: Optional[int] = Field(default=None, primary_key=True)
    text: Optional[str]
    image_path: Optional[str] = Field(
        sa_column=Column(ImageType(storage=storage)),
    )
    url_link: Optional[str]
    is_active: bool
    views_count: int = Field(
        default=0,
        sa_column=Column(Integer, nullable=False, server_default="0"),
        description='Количество просмотров контента',
    )
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

    telegram_id: Optional[int] = Field(
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
    answer: Optional[str]

    user_id: int = Field(foreign_key=f'{User.__tablename__}.telegram_id')
    user: User = Relationship(
        back_populates='questions',
        sa_relationship_kwargs={'lazy': 'selectin'},
    )
