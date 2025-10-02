"""
Админские обработчики для управления контентом.
"""
import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.db import get_session
from data.models import Content, Category
from data.queries import get_button_by_id, get_category_by_id
from sqlmodel import select

from ..keyboards.callbacks import (
    AdminCallback,
    AdminCategoryCallback,
    AdminContentCallback,
    AdminContentActionCallback,
    UserStates
)
from utils.url_utils import clean_url, is_valid_image_url

logger = logging.getLogger(__name__)

admin_router = Router()


@admin_router.callback_query(AdminCallback.filter(F.action == "manage_content"))
async def handle_admin_manage_content(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Управление контентом' для админа."""
    try:
        await state.set_state(UserStates.ADMIN_CATEGORY_VIEW)

        async with get_session() as session:
            keyboard = await get_admin_main_menu_keyboard(session)

            await callback.message.edit_text(
                "🔧 <b>Управление контентом</b>\n\n"
                "Выберите категорию для управления контентом:",
                reply_markup=keyboard,
                parse_mode="HTML"
            )

        await callback.answer()

    except Exception as e:
        logger.exception(f"Admin manage content error: {e}")
        await callback.answer("❌ Ошибка при загрузке категорий", show_alert=True)


@admin_router.callback_query(AdminCategoryCallback.filter())
async def handle_admin_category_selection(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора категории админом."""
    try:
        callback_data = AdminCategoryCallback.unpack(callback.data)
        category_id = callback_data.category_id

        await state.set_state(UserStates.ADMIN_CONTENT_VIEW)

        async with get_session() as session:
            category = await get_category_by_id(category_id, session)

            if not category:
                await callback.answer("❌ Категория не найдена", show_alert=True)
                return

            keyboard = await get_admin_category_buttons_keyboard(category_id, session)

            await callback.message.edit_text(
                f"📂 <b>{category.title}</b>\n\n"
                "Выберите контент для управления:",
                reply_markup=keyboard,
                parse_mode="HTML"
            )

        await callback.answer()

    except Exception as e:
        logger.exception(f"Admin category selection error: {e}")
        await callback.answer("❌ Ошибка при загрузке контента", show_alert=True)


@admin_router.callback_query(AdminContentCallback.filter())
async def handle_admin_content_selection(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора контента админом."""
    try:
        callback_data = AdminContentCallback.unpack(callback.data)
        content_id = callback_data.content_id

        await state.set_state(UserStates.ADMIN_CONTENT_MANAGE)

        async with get_session() as session:
            content = await get_button_by_id(content_id, session)

            if not content:
                await callback.answer("❌ Контент не найден", show_alert=True)
                return

            # Создаем клавиатуру с действиями
            builder = InlineKeyboardBuilder()
            builder.button(
                text="👁 Просмотреть",
                callback_data=AdminContentActionCallback(
                    action="view", 
                    content_id=content_id
                ).pack()
            )
            builder.button(
                text="📷 Изменить изображение",
                callback_data=AdminContentActionCallback(
                    action="upload_image", 
                    content_id=content_id
                ).pack()
            )
            builder.button(
                text="🔙 Назад к контенту",
                callback_data=AdminCategoryCallback(category_id=content.category_id).pack()
            )
            builder.adjust(1)

            await callback.message.edit_text(
                f"📄 <b>{content.title}</b>\n\n"
                "Что хотите сделать с этим контентом?",
                reply_markup=builder.as_markup(),
                parse_mode="HTML"
            )

        await callback.answer()

    except Exception as e:
        logger.exception(f"Admin content selection error: {e}")
        await callback.answer("❌ Ошибка при загрузке контента", show_alert=True)


@admin_router.callback_query(AdminContentActionCallback.filter())
async def handle_admin_content_action(callback: CallbackQuery, state: FSMContext):
    """Обработчик действий с контентом."""
    try:
        callback_data = AdminContentActionCallback.unpack(callback.data)
        action = callback_data.action
        content_id = callback_data.content_id

        async with get_session() as session:
            content = await get_button_by_id(content_id, session)

            if not content:
                await callback.answer("❌ Контент не найден", show_alert=True)
                return

            if action == "view":
                # Показываем контент как обычному пользователю
                text = f"<b>{content.title}</b>\n\n{content.description}"

                if content.url_link:
                    text += f'\n\n<a href="{content.url_link}">📖 Подробнее</a>'

                builder = InlineKeyboardBuilder()
                builder.button(
                    text="🔙 Назад к управлению",
                    callback_data=AdminContentCallback(content_id=content_id).pack()
                )

                # Используем file_id если доступен, иначе URL
                if content.file_id:
                    logger.info(f"Attempting to display image for content {content_id} using file_id: {content.file_id}")
                    try:
                        await callback.message.edit_media(
                            media=InputMediaPhoto(
                                media=content.file_id,
                                caption=text,
                                parse_mode="HTML"
                            ),
                            reply_markup=builder.as_markup()
                        )
                        logger.info(f"Successfully displayed image for content {content_id}")
                    except Exception as e:
                        logger.warning(f"Failed to edit media for content {content_id}, falling back to photo: {e}")
                        # Fallback: отправляем новое сообщение с изображением
                        try:
                            await callback.message.answer_photo(
                                photo=content.file_id,
                                caption=text,
                                reply_markup=builder.as_markup(),
                                parse_mode="HTML"
                            )
                            await callback.message.delete()
                            logger.info(f"Successfully sent photo for content {content_id}")
                        except Exception as e2:
                            logger.warning(f"Failed to send photo for content {content_id}, falling back to text: {e2}")
                            await callback.message.edit_text(
                                text,
                                reply_markup=builder.as_markup(),
                                parse_mode="HTML",
                                disable_web_page_preview=True
                            )
                            logger.info(f"Successfully displayed text for content {content_id}")
                elif content.image_url:
                    # Очищаем URL изображения перед проверкой
                    image_url = clean_url(content.image_url)

                    if image_url and image_url.strip() and is_valid_image_url(image_url):
                        logger.info(f"Attempting to display image for content {content_id} using URL: {image_url}")
                        try:
                            await callback.message.edit_media(
                                media=InputMediaPhoto(
                                    media=image_url,
                                    caption=text,
                                    parse_mode="HTML"
                                ),
                                reply_markup=builder.as_markup()
                            )
                            logger.info(f"Successfully displayed image for content {content_id}")
                        except Exception as e:
                            logger.warning(f"Failed to edit media for content {content_id}, falling back to photo: {e}")
                            # Fallback: отправляем новое сообщение с изображением
                            try:
                                await callback.message.answer_photo(
                                    photo=image_url,
                                    caption=text,
                                    reply_markup=builder.as_markup(),
                                    parse_mode="HTML"
                                )
                                await callback.message.delete()
                                logger.info(f"Successfully sent photo for content {content_id}")
                            except Exception as e2:
                                logger.warning(f"Failed to send photo for content {content_id}, falling back to text: {e2}")
                                await callback.message.edit_text(
                                    text,
                                    reply_markup=builder.as_markup(),
                                    parse_mode="HTML",
                                    disable_web_page_preview=True
                                )
                                logger.info(f"Successfully displayed text for content {content_id}")
                    else:
                        # Если есть image_url, но он невалидный, добавляем информацию
                        if content.image_url and content.image_url.strip():
                            text += f"\n\n⚠️ <i>Изображение недоступно: {content.image_url}</i>"
                            logger.warning(f"Invalid image URL for content {content_id}: {content.image_url}")
                        
                        await callback.message.edit_text(
                            text,
                            reply_markup=builder.as_markup(),
                            parse_mode="HTML",
                            disable_web_page_preview=True
                        )
                else:
                    # Нет изображения
                    await callback.message.edit_text(
                        text,
                        reply_markup=builder.as_markup(),
                        parse_mode="HTML",
                        disable_web_page_preview=True
                    )

            elif action == "upload_image":
                # Переходим к загрузке изображения
                await state.set_state(UserStates.UPLOADING_IMAGE)
                await state.update_data(content_id=content_id)
                
                await callback.message.edit_text(
                    f"📷 <b>Загрузка изображения для контента:</b> {content.title}\n\n"
                    "Отправьте изображение, которое будет отображаться с этим контентом.\n"
                    "Изображение будет сохранено как URL.",
                    parse_mode="HTML"
                )

        await callback.answer()

    except Exception as e:
        logger.exception(f"Admin content action error: {e}")
        await callback.answer("❌ Ошибка при выполнении действия", show_alert=True)


@admin_router.message(UserStates.UPLOADING_IMAGE, F.photo)
async def handle_image_upload(message: Message, state: FSMContext):
    """Обработчик загрузки изображения."""
    try:
        data = await state.get_data()
        content_id = data.get('content_id')

        if not content_id:
            await message.answer("❌ Ошибка: не найден ID контента")
            await state.clear()
            return

        # Получаем информацию о фото
        photo = message.photo[-1]
        file_id = photo.file_id

        # Получаем информацию о файле
        file_info = await message.bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file_info.file_path}"

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
            url_status = "✅ Валидный URL" if is_valid_image_url(file_url) else "⚠️ URL может быть недоступен"

            await message.answer(
                f"✅ <b>Изображение успешно загружено!</b>\n\n"
                f"Контент: {content.title}\n"
                f"File ID: {file_id}\n"
                f"URL изображения: {file_url}\n"
                f"Статус: {url_status}",
                parse_mode="HTML"
            )

        await state.clear()

    except Exception as e:
        logger.exception(f"Image upload error: {e}")
        await message.answer("❌ Ошибка при загрузке изображения")
        await state.clear()


@admin_router.message(UserStates.UPLOADING_IMAGE)
async def handle_non_image_upload(message: Message, state: FSMContext):
    """Обработчик не-изображений во время загрузки изображения."""
    await message.answer(
        "❌ Пожалуйста, отправьте изображение (фото). "
        "Другие типы файлов не поддерживаются."
    )


# Функции для создания клавиатур (перенесены из main_menu.py)
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
            callback_data=AdminCallback(action="manage_content").pack()
        )
        builder.adjust(1)

    except Exception:
        builder.button(
            text="❌ Ошибка загрузки данных",
            callback_data=AdminCallback(action="manage_content").pack(),
        )
        builder.adjust(1)

    return builder.as_markup()
