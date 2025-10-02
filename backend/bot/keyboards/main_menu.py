from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from data.models import Content, Category
from .callbacks import (
    AdminCallback,
    ButtonCallback,
    CategoryCallback,
    FeedbackCallback,
    GoToMainMenuCallback,
    RatingCallback
)


async def add_back_to_main_menu_button(builder: InlineKeyboardBuilder) -> None:
    """
    Добавляет в клавиатуру кнопку "Назад к главному меню".
    """
    builder.button(
        text="🔙 Назад к главному меню",
        callback_data=GoToMainMenuCallback().pack()
    )


async def get_main_menu_keyboard(
        session: AsyncSession) -> InlineKeyboardMarkup:
    """
    Создает главное меню с двумя основными категориями из БД.
    """
    builder = InlineKeyboardBuilder()
    query = select(Category)
    result = await session.execute(query)
    categories = result.scalars().all()
    for category in categories:
        builder.button(
            text=category.title,
            callback_data=CategoryCallback(category_id=category.id).pack(),
        )
    builder.adjust(1)
    return builder.as_markup()


async def get_category_buttons_keyboard(
    category_id: int, session: AsyncSession
) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками для конкретной категории.
    """
    builder = InlineKeyboardBuilder()
    try:
        query = select(Content).where(Content.category_id == category_id)
        result = await session.execute(query)
        buttons = result.scalars().all()

        for button in buttons:
            builder.button(
                text=button.title,
                callback_data=ButtonCallback(button_id=button.id).pack(),
            )

        builder.button(
            text="🔙 Назад к главному меню",
            callback_data=GoToMainMenuCallback().pack()
        )
        builder.adjust(1)

    except Exception:
        builder.button(
            text="❌ Ошибка загрузки данных",
            callback_data=GoToMainMenuCallback().pack(),
        )
        builder.adjust(1)

    return builder.as_markup()


async def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает реплай-клавиатуру с кнопками «Помощь»,
    «Задать вопрос» и Полезные материалы»
    """
    builder = ReplyKeyboardBuilder()
    builder.button(text="🤝 Помощь")
    builder.button(text="❓ Задать вопрос")
    builder.button(text="🗒 Полезные материалы")
    builder.button(text="✅ К выбору категории")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


async def get_admin_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает реплай-клавиатуру для админов с кнопками:
    - Админ панель
    - Отправка напоминаний
    """
    builder = ReplyKeyboardBuilder()
    builder.button(text="🔗 Админ панель")
    builder.button(text="📢 Напоминания")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


async def get_admin_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Создает inline клавиатуру для админов с кнопками:
    - К вопросам
    - К статистике
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="❓ К вопросам",
        url="https://stepaxvii.ru/admin/question/list"
    )
    builder.button(
        text="📊 К статистике",
        url="https://stepaxvii.ru/admin/interactionevent/list"
    )
    builder.adjust(1)
    return builder.as_markup()


async def get_reminder_type_keyboard() -> InlineKeyboardMarkup:
    """
    Создает inline клавиатуру для выбора типа напоминания
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="От бота",
        callback_data=AdminCallback(
            action="send_reminder",
            question_id=None,
            reminder_type="bot"
        ).pack()
    )
    builder.button(
        text="От Аури",
        callback_data=AdminCallback(
            action="send_reminder",
            question_id=None,
            reminder_type="auri"
        ).pack()
    )
    builder.button(
        text="Отмена",
        callback_data=AdminCallback(
            action="cancel",
            question_id=None,
            reminder_type=None
        ).pack()
    )
    builder.adjust(1)
    return builder.as_markup()


async def get_admin_answer_keyboard(question_id: int) -> InlineKeyboardMarkup:
    """Кнопка 'Ответить' для админа."""
    builder = InlineKeyboardBuilder()
    builder.button(
            text="Ответить",
            callback_data=AdminCallback(
                action="answer_question",
                question_id=question_id,
                reminder_type=None
            ).pack()
    )
    builder.adjust(1)
    return builder.as_markup()


def get_feedback_keyboard(
        content_id: int,
        category_id: int
        ) -> InlineKeyboardMarkup:
    """
    Создает и возвращает клавиатуру для обратной связи и навигации.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Было полезно 👍",
            callback_data=FeedbackCallback(
                action="helpful",
                content_id=content_id).pack()
        ),
        InlineKeyboardButton(
            text="Не помогло 👎",
            callback_data=FeedbackCallback(
                action="unhelpful",
                content_id=content_id).pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=CategoryCallback(
                category_id=category_id).pack()
        )
    )
    return builder.as_markup()


def get_rating_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для оценки от 1 до 5."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="5 ⭐",
        callback_data=RatingCallback(rating=5).pack()
    )
    builder.button(
        text="4 ⭐",
        callback_data=RatingCallback(rating=5).pack()
    )
    builder.button(
        text="3 ⭐",
        callback_data=RatingCallback(rating=5).pack()
    )
    builder.button(
        text="2 ⭐",
        callback_data=RatingCallback(rating=5).pack()
    )
    builder.button(
        text="1 ⭐",
        callback_data=RatingCallback(rating=5).pack()
    )
    builder.adjust(5)
    return builder.as_markup()
