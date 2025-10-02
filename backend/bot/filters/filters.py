from aiogram import F
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from bot.config import ADMINS


class IsAdminFilter(BaseFilter):
    """Фильтр для проверки, является ли пользователь администратором."""

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in ADMINS


class IsUserFilter(BaseFilter):
    """Фильтр для проверки, что пользователь не администратор."""

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id not in ADMINS


class TextFilter(BaseFilter):
    """Фильтр для проверки текста сообщения."""

    def __init__(self, text: str):
        self.text = text

    async def __call__(self, message: Message) -> bool:
        return message.text == self.text


class CallbackDataFilter(BaseFilter):
    """Фильтр для проверки callback данных."""

    def __init__(self, prefix: str):
        self.prefix = prefix

    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.data and callback.data.startswith(self.prefix)


class Filters:
    """Предустановленные фильтрами."""

    # Админские фильтры
    IS_ADMIN = IsAdminFilter()
    IS_USER = IsUserFilter()

    # Текстовые фильтры
    HELP_BUTTON = TextFilter("🤝 Помощь")
    QUESTION_BUTTON = TextFilter("❓ Задать вопрос")
    MATERIALS_BUTTON = TextFilter("🗒 Полезные материалы")
    CATEGORIES_BUTTON = TextFilter("✅ К выбору категории")
    ADMIN_PANEL_BUTTON = TextFilter("🔗 Админ панель")
    REMINDERS_BUTTON = TextFilter("📢 Напоминания")

    # Callback фильтры
    CATEGORY_CALLBACK = CallbackDataFilter("category:")
    BUTTON_CALLBACK = CallbackDataFilter("button:")
    FEEDBACK_CALLBACK = CallbackDataFilter("feedback:")
    RATING_CALLBACK = CallbackDataFilter("rating:")
    ADMIN_CALLBACK = CallbackDataFilter("admin:")

    # Комбинированные фильтры
    ADMIN_MESSAGE = F.text.in_([
        "🔗 Админ панель",
        "📢 Напоминания"
    ])

    USER_MESSAGE = F.text.in_([
        "🤝 Помощь",
        "❓ Задать вопрос", 
        "🗒 Полезные материалы",
        "✅ К выбору категории"
    ])
