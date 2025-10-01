from typing import Optional
from datetime import datetime, timedelta

from sqlalchemy import DateTime, String, Text
from sqlmodel import Field, SQLModel

from enums.fields import Length


class BaseIDMixin(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)


class BaseInfoMixin(SQLModel):
    title: str = Field(
        sa_type=String(length=Length.TITLE_FIELD.value),
        unique=True,
        nullable=False,
    )
    description: Optional[str] = Field(
        sa_type=Text(length=Length.TEXT_FIELD.value),
    )


class BaseCreatedAtFieldMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(hours=3),
        sa_type=DateTime(timezone=True),
    )
