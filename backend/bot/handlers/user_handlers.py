from logging import getLogger
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.db import get_session
from data.queries import (
    get_button_by_id,
    get_category_by_id,
    get_or_create_user,
)
from bot.config import ADMINS
from bot.urls import URLs, URLBuilder
from bot.keyboards.callbacks import (
    CategoryCallback,
    ButtonCallback,
    FeedbackCallback,
    RatingCallback,
    UserStates
)
from bot.keyboards.main_menu import (
    get_category_buttons_keyboard,
    get_feedback_keyboard,
    get_main_menu_keyboard,
    get_rating_keyboard,
)
from bot.services.content_service import ContentService
from bot.services.question_service import QuestionService
from bot.services.rating_service import RatingService
from bot.filters import Filters
from bot.utils import safe_edit_message, safe_delete_and_send

logger = getLogger(__name__)
user_router = Router()


@user_router.callback_query(F.data.startswith("category:"))
async def handle_category_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка callback для выбора категории"""
    try:
        callback_data = CategoryCallback.unpack(callback.data)
        logger.info(
            f"Category selected: {callback_data.category_id} "
            f"by user {callback.from_user.id}"
        )

        await state.set_state(UserStates.CATEGORY_VIEW)

        async with get_session() as session:
            category = await get_category_by_id(
                callback_data.category_id,
                session
            )

            if not category:
                logger.warning(
                    "Category not found: "
                    f"{callback_data.category_id}"
                )
                await callback.answer(
                    "❌ Категория не найдена",
                    show_alert=True
                )
                return

            keyboard = await get_category_buttons_keyboard(
                callback_data.category_id, session
            )

            await safe_delete_and_send(
                callback,
                f"📂 {category.title}\n\n"
                f"{(category.description or 'Выберите интересующий вас раздел:')}",
                reply_markup=keyboard,
            )

        await callback.answer()

    except Exception as e:
        logger.exception(
            f"Category callback error: {e} "
            f"(user: {callback.from_user.id})"
        )
        await callback.answer("❌ Ошибка обработки запроса", show_alert=True)


@user_router.callback_query(F.data == "go_main")
async def handle_go_to_main_menu_callback(
    callback: CallbackQuery,
    state: FSMContext
):
    """Обработка callback для возврата в главное меню"""
    try:
        logger.info(f"Go to main menu: {callback.from_user.id}")

        await state.set_state(UserStates.MAIN_MENU)

        async with get_session() as session:
            keyboard = await get_main_menu_keyboard(session)
            await safe_delete_and_send(
                callback,
                "🏠 Главное меню\n\nВыберите интересующую вас категорию:",
                reply_markup=keyboard,
            )

        await callback.answer()

    except Exception as e:
        logger.exception(
            f"Go to main menu error: {e} "
            f"(user: {callback.from_user.id})"
        )
        await callback.answer("❌ Ошибка обработки запроса", show_alert=True)


@user_router.callback_query(F.data.startswith("button:"))
async def handle_button_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка callback для кнопок контента."""
    try:
        callback_data = ButtonCallback.unpack(callback.data)
        logger.info(
            f"Button selected: {callback_data.button_id} "
            f"by user {callback.from_user.id}"
        )

        await state.set_state(UserStates.BUTTON_CONTENT)

        async with get_session() as session:
            button = await get_button_by_id(callback_data.button_id, session)

            if not button:
                logger.warning(f"Button not found: {callback_data.button_id}")
                await callback.answer("❌ Кнопка не найдена", show_alert=True)
                return

            # Обновляем счетчик просмотров
            button.views_count += 1
            session.add(button)
            await session.commit()
            logger.info(
                f"Updated views for content_id {button.id} "
                f"to {button.views_count}"
            )

            # Отображаем контент
            await ContentService.display_content(
                callback, button, get_feedback_keyboard
            )

        await callback.answer()

    except Exception as e:
        logger.exception(
            f"Button callback error: {e} "
            f"(user: {callback.from_user.id})"
        )
        await callback.answer("❌ Ошибка обработки запроса", show_alert=True)


@user_router.message(F.text == "✅ К выбору категории")
async def show_categories(message: Message, state: FSMContext):
    """
    Обработчик для кнопки 'К выбору категории'.
    Показывает инлайн-клавиатуру с категориями без приветствия.
    """
    logger.info(
        f"User {message.from_user.id} requested categories from main menu"
    )
    await state.set_state(UserStates.MAIN_MENU)
    async with get_session() as session:
        inline_keyboard = await get_main_menu_keyboard(session)
        await message.answer(
            "Выберите интересующую вас категорию:",
            reply_markup=inline_keyboard
        )
    await message.delete()


@user_router.message(Filters.QUESTION_BUTTON)
async def ask_question_start(message: Message, state: FSMContext):
    """
    Обработчик для кнопки 'Задать вопрос'.
    """
    await state.set_state(UserStates.QUESTION)
    await message.answer(
        "Не нашли нужную информацию? "
        "Напишите свой вопрос, и мы передадим его администратору. "
        "В ближайшее время вы получите ответ."
    )
    await message.delete()


@user_router.message(UserStates.QUESTION)
async def process_question(message: Message, state: FSMContext):
    """
    Принимает вопрос, сохраняет в БД, обеспечивает существование пользователя
    и уведомляет администраторов.
    """
    try:
        if not message.text or message.text.startswith('/'):
            await message.answer(
                "Пожалуйста, введите ваш вопрос текстом. "
                "Команды не принимаются.")
            return

        await QuestionService.process_user_question(
            message, state, ADMINS, URLs.ADMIN_QUESTION_URL
        )

    except Exception as e:
        logger.exception(
            "Error processing question from user "
            f"{message.from_user.id}: {e}"
        )
        await message.answer(
            "❌ Произошла ошибка при отправке вашего вопроса. "
            "Пожалуйста, попробуйте еще раз позже."
        )
        await state.clear()


@user_router.message(Filters.HELP_BUTTON)
async def help_request(message: Message):
    """Обрабатывает кнопку 'Помощь'."""
    await message.answer(
        "Мы направили в поддержку обращение, "
        "скоро с вами свяжется администратор."
    )
    await message.delete()


@user_router.message(Filters.MATERIALS_BUTTON)
async def handle_useful_materials(message: Message):
    """Обработчик кнопки 'Полезные материалы'"""
    logger.info(f"Useful materials requested: {message.from_user.id}")

    text = URLBuilder.get_useful_materials_text()
    await message.answer(
        text,
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await message.delete()


@user_router.callback_query(FeedbackCallback.filter())
async def handle_feedback_callback(
    callback: CallbackQuery,
    callback_data: FeedbackCallback,
    state: FSMContext
):
    """Обработка обратной связи (полезно/не помогло)"""
    try:
        user_id = callback.from_user.id
        content_id = callback_data.content_id
        action = callback_data.action

        # Сохраняем обратную связь в БД
        async with get_session() as session:
            user = await get_or_create_user(callback.from_user, session)

            # Проверяем, есть ли уже рейтинг от этого пользователя
            rating_obj = await RatingService.get_or_create_rating(
                user.telegram_id, content_id, session
            )

            # Обновляем рейтинг
            rating_obj.is_helpful = (action == "helpful")
            session.add(rating_obj)
            await session.commit()

            logger.info(f"Feedback saved: user {user_id}, content {content_id}, helpful={action == 'helpful'}")

        if action == "helpful":
            await state.set_state(UserStates.REVIEW)
            # Сохраняем content_id в состоянии для последующего использования
            await state.update_data(content_id=content_id)

            text = (
                "Мы рады, что смогли вам помочь! 😊\n\n"
                "Пожалуйста, оцените материал."
            )
            keyboard = get_rating_keyboard(content_id)
            await safe_delete_and_send(
                callback,
                text,
                reply_markup=keyboard
            )
            await callback.answer()

        elif action == "unhelpful":
            text = (
                "Спасибо за обратную связь! "
                "Мы постараемся улучшить материал. 🙏"
            )
            async with get_session() as session:
                button = await get_button_by_id(content_id, session)
                builder = InlineKeyboardBuilder()
                if button:
                    builder.row(
                        InlineKeyboardButton(
                            text="🔙 Назад",
                            callback_data=CategoryCallback(
                                category_id=button.category_id).pack()
                        )
                    )
                await safe_delete_and_send(
                    callback,
                    text,
                    reply_markup=builder.as_markup()
                )
            await callback.answer()

    except Exception as e:
        logger.exception(
            f"Feedback callback error: {e} "
            f"(user: {callback.from_user.id})"
        )
        await callback.answer(
            "❌ Ошибка обработки обратной связи",
            show_alert=True
        )


@user_router.callback_query(
    UserStates.REVIEW,
    RatingCallback.filter()
)
async def handle_rating_callback(
    callback: CallbackQuery,
    callback_data: RatingCallback,
    state: FSMContext
):
    """Обработка нажатия на кнопку с оценкой ⭐."""
    try:
        user_id = callback.from_user.id
        rating = callback_data.rating
        data = await state.get_data()
        content_id = data.get('content_id')

        if not content_id:
            logger.error(f"Content ID not found in state for user {user_id}")
            await callback.answer(
                "❌ Ошибка: не найден ID контента", 
                show_alert=True
            )
            return

        # Сохраняем оценку в БД
        async with get_session() as session:
            user = await get_or_create_user(callback.from_user, session)

            # Обновляем существующий рейтинг или создаем новый
            rating_obj = await RatingService.get_or_create_rating(
                user.telegram_id, content_id, session
            )

            rating_obj.score = rating
            session.add(rating_obj)
            await session.commit()

            logger.info(f"Rating saved: user {user_id}, content {content_id}, score={rating}")

        await safe_delete_and_send(
            callback,
            text="Спасибо за оценку! ⭐",
            reply_markup=None
        )
        await callback.answer()
        await state.clear()

    except Exception as e:
        logger.exception(
            f"Rating callback error: {e} "
            f"(user: {callback.from_user.id})"
        )
        await callback.answer(
            "❌ Ошибка обработки оценки",
            show_alert=True
        )
