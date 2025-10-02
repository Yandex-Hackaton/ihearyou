from logging import getLogger
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.models import Content
from utils.url_utils import clean_url, is_valid_image_url
from bot.keyboards.callbacks import AdminContentCallback
from bot.utils import safe_edit_message, format_description_with_breaks

logger = getLogger(__name__)


class ContentService:
    """Сервис для работы с контентом."""

    @staticmethod
    async def display_content(callback: CallbackQuery, button: Content, keyboard_func):
        """Отображает контент пользователю."""
        text = f"<b>{button.title}</b>\n\n"

        if button.description:
            # Форматируем описание с разрывами строк после эмодзи
            formatted_description = format_description_with_breaks(
                button.description
            )
            text += f"{formatted_description}\n\n"

        if button.url_link:
            text += f'<a href="{button.url_link}">Ознакомиться подробнее</a>'
        else:
            text += (
                "ℹ️ Информация по данному разделу "
                "будет добавлена в ближайшее время."
            )

        keyboard = keyboard_func(
            content_id=button.id,
            category_id=button.category_id
        )

        # Используем file_id если доступен, иначе URL
        if button.file_id:
            await ContentService._display_with_file_id(callback, button, text, keyboard)
        elif button.image_url:
            await ContentService._display_with_url(callback, button, text, keyboard)
        else:
            # Нет изображения
            await safe_edit_message(
                callback,
                text,
                reply_markup=keyboard,
                parse_mode="HTML",
                disable_web_page_preview=True
            )

    @staticmethod
    async def display_content_for_admin(callback: CallbackQuery, content: Content):
        """Отображает контент для админа."""
        # Форматируем описание с разрывами строк после эмодзи
        formatted_description = format_description_with_breaks(
            content.description
        )
        text = f"<b>{content.title}</b>\n\n{formatted_description}"

        if content.url_link:
            text += f'\n\n<a href="{content.url_link}">📖 Подробнее</a>'

        builder = InlineKeyboardBuilder()
        builder.button(
            text="🔙 Назад к управлению",
            callback_data=AdminContentCallback(content_id=content.id).pack()
        )

        if content.file_id:
            await ContentService._display_with_file_id_admin(callback, content, text, builder)
        elif content.image_url:
            await ContentService._display_with_url_admin(callback, content, text, builder)
        else:
            # Нет изображения
            await safe_edit_message(
                callback,
                text,
                reply_markup=builder.as_markup(),
                parse_mode="HTML",
                disable_web_page_preview=True
            )

    @staticmethod
    async def _display_with_file_id(callback: CallbackQuery, button: Content, text: str, keyboard):
        """Отображает контент с file_id."""
        logger.info(f"Displaying image for content {button.id} using file_id: {button.file_id}")
        try:
            await callback.message.edit_media(
                media=InputMediaPhoto(
                    media=button.file_id,
                    caption=text,
                    parse_mode="HTML"
                ),
                reply_markup=keyboard
            )
            logger.info(f"Successfully displayed image for content {button.id}")
        except Exception as e:
            logger.warning(f"Failed to edit media for content {button.id}, falling back to photo: {e}")
            # Fallback: отправляем новое сообщение с изображением
            try:
                await callback.message.answer_photo(
                    photo=button.file_id,
                    caption=text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
                await callback.message.delete()
                logger.info(f"Successfully sent photo for content {button.id}")
            except Exception as e2:
                logger.warning(f"Failed to send photo for content {button.id}, falling back to text: {e2}")
                await safe_edit_message(
                    callback,
                    text,
                    reply_markup=keyboard,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
                logger.info(f"Successfully displayed text for content {button.id}")

    @staticmethod
    async def _display_with_url(callback: CallbackQuery, button: Content, text: str, keyboard):
        """Отображает контент с URL изображения."""
        image_url = clean_url(button.image_url)

        if image_url and image_url.strip() and is_valid_image_url(image_url):
            logger.info(f"Displaying image for content {button.id} using URL: {image_url}")
            try:
                await callback.message.edit_media(
                    media=InputMediaPhoto(
                        media=image_url,
                        caption=text,
                        parse_mode="HTML"
                    ),
                    reply_markup=keyboard
                )
                logger.info(f"Successfully displayed image for content {button.id}")
            except Exception as e:
                logger.warning(f"Failed to edit media for content {button.id}, falling back to photo: {e}")
                try:
                    await callback.message.answer_photo(
                        photo=image_url,
                        caption=text,
                        reply_markup=keyboard,
                        parse_mode="HTML"
                    )
                    await callback.message.delete()
                    logger.info(f"Successfully sent photo for content {button.id}")
                except Exception as e2:
                    logger.warning(f"Failed to send photo for content {button.id}, falling back to text: {e2}")
                    await safe_edit_message(
                        callback,
                        text,
                        reply_markup=keyboard,
                        parse_mode="HTML",
                        disable_web_page_preview=True
                    )
                    logger.info(f"Successfully displayed text for content {button.id}")
        else:
            logger.warning(f"Invalid image URL for content {button.id}: {button.image_url}")
            await safe_edit_message(
                callback,
                text,
                reply_markup=keyboard,
                parse_mode="HTML",
                disable_web_page_preview=True
            )

    @staticmethod
    async def _display_with_file_id_admin(callback: CallbackQuery, content: Content, text: str, builder):
        """Отображает контент с file_id для админа."""
        logger.info(f"Attempting to display image for content {content.id} using file_id: {content.file_id}")
        try:
            await callback.message.edit_media(
                media=InputMediaPhoto(
                    media=content.file_id,
                    caption=text,
                    parse_mode="HTML"
                ),
                reply_markup=builder.as_markup()
            )
            logger.info(f"Successfully displayed image for content {content.id}")
        except Exception as e:
            logger.warning(f"Failed to edit media for content {content.id}, falling back to photo: {e}")
            try:
                await callback.message.answer_photo(
                    photo=content.file_id,
                    caption=text,
                    reply_markup=builder.as_markup(),
                    parse_mode="HTML"
                )
                await callback.message.delete()
                logger.info(f"Successfully sent photo for content {content.id}")
            except Exception as e2:
                logger.warning(f"Failed to send photo for content {content.id}, falling back to text: {e2}")
                await safe_edit_message(
                    callback,
                    text,
                    reply_markup=builder.as_markup(),
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
                logger.info(f"Successfully displayed text for content {content.id}")

    @staticmethod
    async def _display_with_url_admin(callback: CallbackQuery, content: Content, text: str, builder):
        """Отображает контент с URL изображения для админа."""
        image_url = clean_url(content.image_url)

        if image_url and image_url.strip() and is_valid_image_url(image_url):
            logger.info(f"Attempting to display image for content {content.id} using URL: {image_url}")
            try:
                await callback.message.edit_media(
                    media=InputMediaPhoto(
                        media=image_url,
                        caption=text,
                        parse_mode="HTML"
                    ),
                    reply_markup=builder.as_markup()
                )
                logger.info(f"Successfully displayed image for content {content.id}")
            except Exception as e:
                logger.warning(f"Failed to edit media for content {content.id}, falling back to photo: {e}")
                try:
                    await callback.message.answer_photo(
                        photo=image_url,
                        caption=text,
                        reply_markup=builder.as_markup(),
                        parse_mode="HTML"
                    )
                    await callback.message.delete()
                    logger.info(f"Successfully sent photo for content {content.id}")
                except Exception as e2:
                    logger.warning(f"Failed to send photo for content {content.id}, falling back to text: {e2}")
                    await safe_edit_message(
                        callback,
                        text,
                        reply_markup=builder.as_markup(),
                        parse_mode="HTML",
                        disable_web_page_preview=True
                    )
                    logger.info(f"Successfully displayed text for content {content.id}")
        else:
            if content.image_url and content.image_url.strip():
                text += f"\n\n⚠️ <i>Изображение недоступно: {content.image_url}</i>"
                logger.warning(f"Invalid image URL for content {content.id}: {content.image_url}")

            await safe_edit_message(
                callback,
                text,
                reply_markup=builder.as_markup(),
                parse_mode="HTML",
                disable_web_page_preview=True
            )
