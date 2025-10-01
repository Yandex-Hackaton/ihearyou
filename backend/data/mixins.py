from typing import Optional
from datetime import datetime, timedelta

from sqlalchemy import DateTime, String, Text
from sqlmodel import Field, SQLModel

from .constants import (
    TITLE_FIELD_MX_LEN,
    DESC_FIELD_MX_LEN,
)


class BaseInfoMixin(SQLModel):
    title: str = Field(
        sa_type=String(length=TITLE_FIELD_MX_LEN),
        unique=True,
        nullable=False,
    )
    description: Optional[str] = Field(
        sa_type=Text(length=DESC_FIELD_MX_LEN),
    )


class BaseCreatedAtFieldMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(hours=3),
        sa_type=DateTime(timezone=True),
    )
