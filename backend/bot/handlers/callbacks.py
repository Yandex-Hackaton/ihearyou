from aiogram import Router

from bot.handlers.user_handlers import user_router
from bot.handlers.admin_handlers import admin_router
from bot.handlers.chat_events import chat_events_router


callback_router = Router()

callback_router.include_router(user_router)
callback_router.include_router(admin_router)
callback_router.include_router(chat_events_router)
