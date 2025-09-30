from typing import Optional

from sqlmodel import Field


class BaseInfoMixin:
    title: str = Field(unique=True)
    description: Optional[str]
