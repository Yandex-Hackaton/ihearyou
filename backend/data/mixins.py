from typing import Optional
from datetime import datetime

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field


class BaseInfoMixin:
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(unique=True)
    description: Optional[str]
