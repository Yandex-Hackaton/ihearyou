from typing import Optional
from datetime import date

from sqlmodel import SQLModel, Relationship, Field

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Role(SQLModel, table=True):
    __tablename__ = 'users_roles'

    id: Optional[int] = Field(default=None, primary_key=True,)
    slug: str = Field(unique=True,)
    title: str = Field(unique=True)
    description: Optional[str]

    users: list['User'] = Relationship(
        back_populates='role',
        sa_relationship_kwargs={'lazy': 'selectin'},
    )
    categories: list['Category'] = Relationship(
        back_populates='for_user_role',
        sa_relationship_kwargs={'lazy': 'selectin'},
    )


class Category(SQLModel, table=True):
    __tablename__ = 'buttons_categories'

    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(unique=True)
    title: str = Field(unique=True)
    description: Optional[str]

    for_user_role_id: int = Field(foreign_key=f'{Role.__tablename__}.id')
    for_user_role: Role = Relationship(back_populates='categories')

    buttons: list['Button'] = Relationship(
        back_populates='category',
        sa_relationship_kwargs={'lazy': 'selectin'},
    )


class Button(SQLModel, table=True):
    __tablename__ = 'buttons'

    id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
    title: str = Field(unique=True, index=True)
    description: Optional[str]
    content: Optional[str]

    category_id: int = Field(foreign_key=f'{Category.__tablename__}.id')
    category: Category = Relationship(back_populates='buttons')


class User(SQLModel, table=True):
    __tablename__ = 'users'

    id: Optional[int] = Field(default=None, primary_key=True,)
    username: str = Field(unique=True, index=True)
    password: str
    name: Optional[str] = Field(index=True)
    surname: Optional[str] = Field(index=True)
    patronymic: Optional[str] = Field(index=True)
    birth_date: Optional[date]

    role_id: int = Field(foreign_key=f'{Role.__tablename__}.id')
    role: Role = Relationship(
        back_populates='users',
        sa_relationship_kwargs={'lazy': 'selectin'},
    )

    @property
    def full_name(self) -> str:
        return f"{self.name} {self.surname}"
