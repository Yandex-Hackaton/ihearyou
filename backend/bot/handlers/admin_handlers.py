from logging import getLogger
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.db import get_session
from data.queries import get_button_by_id, get_category_by_id
from bot.keyboards.callbacks import (
    AdminCallback,
    AdminCategoryCallback,
    AdminContentCallback,
    AdminContentActionCallback,
    UserStates
)
from bot.keyboards.main_menu import (
    get_admin_inline_keyboard,
    get_reminder_type_keyboard,
)
from bot.services.admin_service import AdminService
from bot.services.content_service import ContentService
from bot.services.question_service import QuestionService
from bot.services.reminder_service import ReminderService
from bot.urls import URLBuilder
from bot.filters import Filters
from bot.utils import safe_edit_message, safe_delete_and_send

logger = getLogger(__name__)
admin_router = Router()


@admin_router.message(Filters.ADMIN_PANEL_BUTTON)
async def admin_panel_menu(message: Message):
    """Обрабатывает кнопку 'Админ панель' для админов."""

    keyboard = await get_admin_inline_keyboard()
    await message.answer(
        "Перейти в админ-панель:",
        reply_markup=keyboard
    )
    await message.delete()


@admin_router.message(Filters.REMINDERS_BUTTON)
async def send_reminders_menu(message: Message):
    """Обрабатывает кнопку 'Напоминания' для админов."""

    keyboard = await get_reminder_type_keyboard()
    await message.answer(
        "📢 Выберите тип напоминания для отправки пользователям, "
        "которые не пользовались ботом неделю:",
        reply_markup=keyboard
    )
    await message.delete()


@admin_router.callback_query(
    AdminCallback.filter(F.action == "send_reminder")
)
async def send_reminder_callback(
    callback: CallbackQuery, callback_data: AdminCallback
):
    """Обрабатывает отправку напоминаний."""

    reminder_type = callback_data.reminder_type

    # Тексты напоминаний
    reminders = URLBuilder.get_reminder_texts()

    reminder_text = reminders.get(reminder_type, "Неизвестный тип напоминания")

    # Показываем сообщение о начале отправки
    await safe_edit_message(
        callback,
        "Отправляем напоминания неактивным пользователям..."
    )

    try:
        # Отправляем напоминания неактивным пользователям
        results = await ReminderService.send_reminders_to_inactive_users(
            bot=callback.bot,
            reminder_text=reminder_text,
            days=7
        )

        # Формируем сообщение с результатами
        result_message = (
            f"Напоминания отправлены!\n\n"
            f"Статистика:\n"
            f"• Всего неактивных пользователей: {results['total']}\n"
            f"• Успешно отправлено: {results['sent']}\n"
            f"• Ошибок: {results['failed']}"
        )

        if results['errors']:
            result_message += "\n\nОшибки:\n" + "\n".join(results['errors'][:5])
            if len(results['errors']) > 5:
                result_message += (
                    f"\n... и еще {len(results['errors']) - 5} ошибок"
                )
        await safe_edit_message(callback, result_message)

    except Exception as e:
        logger.error(f"Ошибка при отправке напоминаний: {e}")
        await safe_edit_message(
            callback,
            "Ошибка при отправке напоминаний"
        )


@admin_router.callback_query(AdminCallback.filter(F.action == "cancel"))
async def cancel_admin_action(callback: CallbackQuery):
    """Отменяет действие админа."""
    await callback.message.delete()


@admin_router.callback_query(
    AdminCallback.filter(F.action == "answer_question")
)
async def start_answer(
    query: CallbackQuery,
    callback_data: AdminCallback,
    state: FSMContext
):
    """
    Обрабатывает нажатие админом кнопки 'Ответить'.
    Переводит админа в состояние ожидания ответа.
    """
    question_id = callback_data.question_id
    await state.update_data(question_id=question_id)
    await state.set_state(UserStates.ANSWER)
    await query.message.answer(f"Введите ответ на вопрос #{question_id}:")
    await query.answer()


@admin_router.message(UserStates.ANSWER)
async def process_answer(message: Message, state: FSMContext):
    """
    Принимает ответ от админа, сохраняет в БД и отправляет пользователю.
    """
    if not message.text:
        await message.answer("Пожалуйста, введите ответ текстом.")
        return

    await QuestionService.process_admin_answer(message, state)


@admin_router.callback_query(AdminCallback.filter(F.action == "manage_content"))
async def handle_admin_manage_content(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Управление контентом' для админа."""
    try:
        await state.set_state(UserStates.ADMIN_CATEGORY_VIEW)

        async with get_session() as session:
            keyboard = await AdminService.get_admin_main_menu_keyboard(session)

            await safe_delete_and_send(
                callback,
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

            keyboard = await AdminService.get_admin_category_buttons_keyboard(
                category_id, session
            )

            text = (
                f"📂 <b>{category.title}</b>\n\n"
                "Выберите контент для управления:"
            )
            await safe_delete_and_send(
                callback,
                text,
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
                callback_data=AdminCategoryCallback(
                    category_id=content.category_id
                ).pack()
            )
            builder.adjust(1)

            text = (
                f"📄 <b>{content.title}</b>\n\n"
                "Что хотите сделать с этим контентом?"
            )
            await safe_delete_and_send(
                callback,
                text,
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
                await ContentService.display_content_for_admin(callback, content)
            elif action == "upload_image":
                await AdminService.start_image_upload(
                    callback, state, content
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

        await AdminService.process_image_upload(
            message, state, content_id
        )

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
