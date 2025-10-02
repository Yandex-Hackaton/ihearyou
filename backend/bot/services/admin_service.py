from logging import getLogger
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlmodel import select

from data.db import get_session
from data.models import Content, Category
from data.queries import get_button_by_id
from bot.keyboards.callbacks import (
    AdminCallback,
    AdminCategoryCallback,
    AdminContentCallback,
    UserStates
)
from bot.urls import URLBuilder
from utils.url_utils import clean_url, is_valid_image_url
from bot.utils import safe_edit_message, validate_photo, BotValidators

logger = getLogger(__name__)


class AdminService:
    """Сервис для админских функций."""

    @staticmethod
    async def get_admin_main_menu_keyboard(session) -> InlineKeyboardBuilder:
        """
        Создает главное меню с категориями для админской панели.
        """
        builder = InlineKeyboardBuilder()
        query = select(Category).where(Category.is_active)
        result = await session.execute(query)
        categories = result.scalars().all()
        for category in categories:
            builder.button(
                text=category.title,
                callback_data=AdminCategoryCallback(category_id=category.id).pack(),
            )
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def get_admin_category_buttons_keyboard(
        category_id: int, session
    ) -> InlineKeyboardBuilder:
        """
        Создает клавиатуру с кнопками контента для админской панели.
        """
        builder = InlineKeyboardBuilder()
        try:
            query = select(Content).where(
                Content.category_id == category_id,
                Content.is_active
            )
            result = await session.execute(query)
            buttons = result.scalars().all()

            for button in buttons:
                builder.button(
                    text=button.title,
                    callback_data=AdminContentCallback(content_id=button.id).pack(),
                )

            builder.button(
                text="🔙 Назад к категориям",
                callback_data=AdminCallback(
                    action="manage_content"
                ).pack()
            )
            builder.adjust(1)

        except Exception:
            builder.button(
                text="❌ Ошибка загрузки данных",
                callback_data=AdminCallback(action="manage_content").pack(),
            )
            builder.adjust(1)

        return builder.as_markup()

    @staticmethod
    async def start_image_upload(
        callback: CallbackQuery, 
        state: FSMContext, 
        content: Content
    ):
        """Начинает процесс загрузки изображения."""
        # Переходим к загрузке изображения
        await state.set_state(UserStates.UPLOADING_IMAGE)
        await state.update_data(content_id=content.id)

        text = (
            f"📷 <b>Загрузка изображения для контента:</b> {content.title}\n\n"
            "Отправьте изображение, которое будет отображаться с этим контентом.\n"
            "Изображение будет сохранено как URL."
        )
        
        await safe_edit_message(callback, text, parse_mode="HTML")

    @staticmethod
    async def process_image_upload(message, state: FSMContext, content_id: int):
        """Обрабатывает загруженное изображение."""
        # Валидация изображения
        validation_result = validate_photo(message, BotValidators.ADMIN_IMAGE)
        if not validation_result.is_valid:
            await message.answer(f"❌ {validation_result.errors[0]}")
            return

        # Получаем информацию о фото
        photo = message.photo[-1]
        file_id = photo.file_id

        # Получаем информацию о файле
        file_info = await message.bot.get_file(file_id)
        file_url = URLBuilder.get_telegram_file_url(message.bot.token, file_info.file_path)

        # Очищаем URL от невидимых символов
        file_url = clean_url(file_url)

        # Сохраняем file_id и URL изображения в базу данных
        async with get_session() as session:
            content = await get_button_by_id(content_id, session)

            if not content:
                await message.answer("❌ Контент не найден")
                await state.clear()
                return

            content.file_id = file_id
            content.image_url = file_url
            session.add(content)
            await session.commit()

            logger.info(f"Image uploaded for content {content_id}: {file_url}")

            # Проверяем валидность URL
            url_status = "✅" if is_valid_image_url(file_url) else "⚠️ URL может быть недоступен"

            await message.answer(
                f"✅ <b>Изображение успешно загружено!</b>\n\n"
                f"Контент: {content.title}\n"
                f"Статус: {url_status}",
                parse_mode="HTML"
            )

        await state.clear()
