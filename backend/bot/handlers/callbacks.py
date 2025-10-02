from datetime import datetime
from logging import getLogger

from aiogram import F, Router
from aiogram.filters import (
    IS_MEMBER,
    IS_NOT_MEMBER,
    ChatMemberUpdatedFilter,
)

from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    ChatMemberUpdated,
    InlineKeyboardButton,
    Message,
)
from aiogram.types import User as TG_User
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select

from data.db import get_session
from data.models import Question, Rating
from data.queries import (
    get_button_by_id,
    get_category_by_id,
    get_or_create_user,
    set_user_active,
    set_user_inactive,
)
from ..config import ADMINS, ADMIN_QUESTION_URL
from ..keyboards.callbacks import (
    AdminCallback,
    ButtonCallback,
    CategoryCallback,
    FeedbackCallback,
    RatingCallback,
    UserStates
)
from ..keyboards.main_menu import (
    get_admin_answer_keyboard,
    get_category_buttons_keyboard,
    get_feedback_keyboard,
    get_main_menu_keyboard,
    get_rating_keyboard,
    get_reminder_type_keyboard,
    get_admin_inline_keyboard
)
from ..services.reminder_service import ReminderService

callback_router = Router()
logger = getLogger(__name__)


@callback_router.callback_query(F.data.startswith("category:"))
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

            await callback.message.edit_text(
                f"📂 {category.title}\n\n"
                f"{(category.description or
                    'Выберите интересующий вас раздел:')}",
                reply_markup=keyboard,
            )

        await callback.answer()

    except Exception as e:
        logger.exception(
            f"Category callback error: {e} " f"(user: {callback.from_user.id})"
        )
        await callback.answer("❌ Ошибка обработки запроса", show_alert=True)


@callback_router.callback_query(F.data == "go_main")
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
            await callback.message.edit_text(
                "🏠 Главное меню\n\n" "Выберите интересующую вас категорию:",
                reply_markup=keyboard,
            )

        await callback.answer()

    except Exception as e:
        logger.exception(
            f"Go to main menu error: {e} "
            f"(user: {callback.from_user.id})"
        )
        await callback.answer("❌ Ошибка обработки запроса", show_alert=True)


@callback_router.callback_query(F.data.startswith("button:"))
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
            button.views_count += 1
            session.add(button)
            await session.commit()
            logger.info(
                f"Updated views for content_id {button.id} "
                f"to {button.views_count}"
            )
            text = f"📌 {button.title}\n\n"

            if button.description:
                text += f"📝 {button.description}\n\n"

            if button.url_link:
                text += f"🔗 {button.url_link}"
            else:
                text += (
                    "ℹ️ Информация по данному разделу "
                    "будет добавлена в ближайшее время."
                )
            keyboard = get_feedback_keyboard(
                content_id=button.id,
                category_id=button.category_id
            )
            await callback.message.edit_text(
                text,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )

        await callback.answer()

    except Exception as e:
        logger.exception(
            f"Button callback error: {e} "
            f"(user: {callback.from_user.id})"
        )
        await callback.answer(
            "❌ Ошибка обработки запроса",
            show_alert=True
        )


@callback_router.message(F.text == "✅ К выбору категории")
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


@callback_router.message(F.text == "❓ Задать вопрос")
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


@callback_router.message(UserStates.QUESTION)
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

        tg_user: TG_User = getattr(message, "from_user")
        async with get_session() as session:
            user = await get_or_create_user(
                tg_user=tg_user, session=session
            )
            new_question = Question(text=message.text, user_id=user.telegram_id)
            session.add(new_question)
            await session.commit()
            await session.refresh(new_question)

            logger.info(
                f"New question #{new_question.id} "
                f"from user {message.from_user.id}"
                f"<i>Ссылка: {ADMIN_QUESTION_URL}{new_question.id}</i>"
            )

            await message.answer(
                "✅ Спасибо! Ваш вопрос отправлен администратору. "
                "Мы сообщим вам, как только поступит ответ."
            )
            await state.clear()
            # Формируем сообщение для админов
            admin_message = (
                f"❓ <b>Новый вопрос #{new_question.id}</b>\n\n"
                f"<b>От пользователя:</b> @{user.username} "
                f"(ID: {user.telegram_id})\n"
                f"<b>Текст вопроса:</b>\n{message.text}"
                f"<i>Ссылка: {ADMIN_QUESTION_URL}{new_question.id}</i>"
            )
            # Отправляем уведомление всем админам
            for admin_id in ADMINS:
                try:
                    await message.bot.send_message(
                        chat_id=admin_id,
                        text=admin_message,
                        reply_markup=await get_admin_answer_keyboard(
                            new_question.id
                        ),
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.exception(
                        "Failed to send question "
                        f"to admin {admin_id}: {e}"
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


@callback_router.message(F.text == "🔗 Админ панель")
async def admin_panel_menu(message: Message):
    """Обрабатывает кнопку 'Админ панель' для админов."""

    keyboard = await get_admin_inline_keyboard()
    await message.answer(
        "Перейти в админ-панель:",
        reply_markup=keyboard
    )
    await message.delete()


@callback_router.message(F.text == "📢 Напоминания")
async def send_reminders_menu(message: Message):
    """Обрабатывает кнопку 'Напоминания' для админов."""

    keyboard = await get_reminder_type_keyboard()
    await message.answer(
        "📢 Выберите тип напоминания для отправки пользователям, "
        "которые не пользовались ботом неделю:",
        reply_markup=keyboard
    )
    await message.delete()


@callback_router.callback_query(
    AdminCallback.filter(F.action == "send_reminder")
)
async def send_reminder_callback(
    callback: CallbackQuery, callback_data: AdminCallback
):
    """Обрабатывает отправку напоминаний."""

    reminder_type = callback_data.reminder_type

    # Тексты напоминаний
    reminders = {
        "bot": (
            "Привет! Напоминаем, что бот «Я Тебя Слышу» всегда рядом.\n"
            "Здесь ты можешь найти статьи, советы и поддержку. "
            "Загляни, когда будет время 🌿\n\n"
            "Как узнать, что снижен слух: "
            "https://www.ihearyou.ru/materials/articles/kak-uznat-chto-snizhen-slukh\n"
            "Влияние потери слуха на семью: "
            "https://www.ihearyou.ru/materials/articles/vliyanie-poteri-slukha-na-semyu"
        ),
        "auri": (
            "👋 Привет, это снова я — Аури!\n"
            "Ты давно не заглядывал в бот, и я немного скучал 💙\n"
            "У меня тут есть новые материалы и советы, которые могут быть "
            "полезны именно тебе. Загляни, когда будет настроение — "
            "я всегда рядом 🌟"
        )
    }

    reminder_text = reminders.get(reminder_type, "Неизвестный тип напоминания")

    # Показываем сообщение о начале отправки
    await callback.message.edit_text(
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
        await callback.message.edit_text(result_message)

    except Exception as e:
        logger.error(f"Ошибка при отправке напоминаний: {e}")
        await callback.message.edit_text(
            "Ошибка при отправке напоминаний"
        )


@callback_router.callback_query(AdminCallback.filter(F.action == "cancel"))
async def cancel_admin_action(callback: CallbackQuery):
    """Отменяет действие админа."""
    await callback.message.delete()


@callback_router.message(F.text == "🤝 Помощь")
async def help_request(message: Message):
    """Обрабатывает кнопку 'Помощь'."""
    await message.answer(
        "Мы направили в поддержку обращение, "
        "скоро с вами свяжется администратор."
    )


@callback_router.callback_query(FeedbackCallback.filter())
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
            existing_rating = await session.execute(
                select(Rating).where(
                    Rating.user_id == user.telegram_id,
                    Rating.content_id == content_id
                )
            )
            rating_obj = existing_rating.scalar_one_or_none()

            if rating_obj:
                # Обновляем существующий рейтинг
                rating_obj.is_helpful = (action == "helpful")
            else:
                # Создаем новый рейтинг
                rating_obj = Rating(
                    user_id=user.telegram_id,
                    content_id=content_id,
                    is_helpful=(action == "helpful")
                )
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
            await callback.message.edit_text(text, reply_markup=keyboard)
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
                await callback.message.edit_text(
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


@callback_router.callback_query(
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
        content_id = callback_data.content_id
        rating = callback_data.rating

        # Сохраняем оценку в БД
        async with get_session() as session:
            user = await get_or_create_user(callback.from_user, session)

            # Обновляем существующий рейтинг или создаем новый
            existing_rating = await session.execute(
                select(Rating).where(
                    Rating.user_id == user.telegram_id,
                    Rating.content_id == content_id
                )
            )
            rating_obj = existing_rating.scalar_one_or_none()

            if rating_obj:
                # Обновляем существующий рейтинг
                rating_obj.score = rating
            else:
                # Создаем новый рейтинг
                rating_obj = Rating(
                    user_id=user.telegram_id,
                    content_id=content_id,
                    score=rating
                )
                session.add(rating_obj)

            await session.commit()

            logger.info(f"Rating saved: user {user_id}, content {content_id}, score={rating}")

        await callback.message.edit_text(
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

@callback_router.callback_query(
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


@callback_router.message(UserStates.ANSWER)
async def process_answer(message: Message, state: FSMContext):
    """
    Принимает ответ от админа, сохраняет в БД и отправляет пользователю.
    """
    if not message.text:
        await message.answer("Пожалуйста, введите ответ текстом.")
        return
    await state.set_state(UserStates.ANSWER)
    data = await state.get_data()
    question_id = data.get("question_id")

    if not question_id:
        await message.answer(
            "Произошла ошибка, не удалось определить вопрос. "
            "Попробуйте снова."
        )
        await state.clear()
        return
    user_id_to_notify = None

    async with get_session() as session:
        stmt = select(Question).where(Question.id == question_id)
        result = await session.execute(stmt)
        question = result.scalar_one_or_none()
        if not question:
            await message.answer(
                f"Вопрос # {question_id} не найден в базе данных."
            )
            await state.clear()
            return
        question.answer_text = message.text
        user_id_to_notify = question.user_id
        await session.commit()
    user_message = (
        "<b>✅ Ответ на ваш вопрос от "
        f"{datetime.now().strftime('%d.%m.%Y %H:%M')}</b>\n\n"
        f"{message.text}"
    )

    try:
        await message.bot.send_message(
            chat_id=user_id_to_notify,
            text=user_message,
            parse_mode="HTML"
        )
        await message.answer(
            f"✅ Ответ на вопрос #{question_id} "
            "успешно отправлен пользователю."
        )
    except Exception as e:
        await message.answer(
            "⚠️ Не удалось отправить ответ пользователю "
            f"{user_id_to_notify}. Ошибка: {e}")
    await state.clear()


@callback_router.my_chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def on_user_leave(event: ChatMemberUpdated):
    """Отмечает пользователя как неактивного при выходе из чата."""
    async with get_session() as session:
        await set_user_inactive(event.from_user.id, session)


@callback_router.my_chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_user_join(event: ChatMemberUpdated):
    """Отмечает пользователя как активного при входе в чат."""
    async with get_session() as session:
        await set_user_active(event.from_user.id, session)
