
from logging import getLogger
from aiogram import Router
from aiogram.filters import (
    IS_MEMBER,
    IS_NOT_MEMBER,
    ChatMemberUpdatedFilter,
)
from aiogram.types import ChatMemberUpdated

from data.db import get_session
from data.queries import set_user_active, set_user_inactive

logger = getLogger(__name__)
chat_events_router = Router()


@chat_events_router.my_chat_member(
    ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER)
)
async def on_user_leave(event: ChatMemberUpdated):
    """Отмечает пользователя как неактивного при выходе из чата."""
    async with get_session() as session:
        await set_user_inactive(event.from_user.id, session)


@chat_events_router.my_chat_member(
    ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER)
)
async def on_user_join(event: ChatMemberUpdated):
    """Отмечает пользователя как активного при входе в чат."""
    async with get_session() as session:
        await set_user_active(event.from_user.id, session)
