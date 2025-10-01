import os
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    Message
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


from ..keyboards.callbacks import (
    MainMenuCallback,
    ButtonCallback,
    FeedbackCallback,
    UserStates,
    CategoryCallback
)
from ..keyboards.main_menu import (
    get_category_buttons_keyboard,
    get_main_menu_keyboard,
    get_admin_answer_keyboard
)
from data.models import Question, User
from data.queries import get_category_by_id, get_button_by_id
from data.db import get_session
from utils.logger import logger

callback_router = Router()

ADMINS = [int(admin_id) for admin_id in os.getenv("ADMINS", "").split(',')]


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
                    f"Category not found: {callback_data.category_id}"
                )
                await callback.answer(
                    "❌ Категория не найдена",
                    show_alert=True
                )
                return

            keyboard = await get_category_buttons_keyboard(
                callback_data.category_id,
                session
            )

            await callback.message.edit_text(
                f"📂 {category.title}\n\n"
                f"{(category.description or
                    'Выберите интересующий вас раздел:')}",
                reply_markup=keyboard
            )

        await callback.answer()

    except Exception as e:
        logger.error(
            f"Category callback error: {e} "
            f"(user: {callback.from_user.id})"
        )
        await callback.answer(
            "❌ Ошибка обработки запроса",
            show_alert=True
        )


@callback_router.callback_query(F.data.startswith("main_menu:"))
async def handle_main_menu_callback(
    callback: CallbackQuery,
    state: FSMContext
):
    """Обработка callback для главного меню"""
    try:
        callback_data = MainMenuCallback.unpack(callback.data)

        if callback_data.category_id == 0:
            logger.info(f"Return to main menu: {callback.from_user.id}")
            await state.set_state(UserStates.MAIN_MENU)

            async with get_session() as session:
                keyboard = await get_main_menu_keyboard(session)
                await callback.message.edit_text(
                    "🏠 Главное меню\n\n"
                    "Выберите интересующую вас категорию:",
                    reply_markup=keyboard
                )

        else:
            await state.set_state(UserStates.CATEGORY_VIEW)

            async with get_session() as session:
                category = await get_category_by_id(
                    callback_data.category_id,
                    session
                )

                if not category:
                    logger.warning(
                        f"Category not found in main menu: "
                        f"{callback_data.category_id}"
                    )
                    await callback.answer(
                        "❌ Категория не найдена",
                        show_alert=True
                    )
                    return

                keyboard = await get_category_buttons_keyboard(
                    callback_data.category_id,
                    session
                )

                await callback.message.edit_text(
                    f"📂 {category.title}\n\n"
                    f"{(category.description or
                        'Выберите интересующий вас раздел:')}",
                    reply_markup=keyboard
                )

        await callback.answer()

    except Exception as e:
        logger.error(
            f"Main menu callback error: {e} "
            f"(user: {callback.from_user.id})"
        )
        await callback.answer(
            "❌ Ошибка обработки запроса",
            show_alert=True
        )


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
                "🏠 Главное меню\n\n"
                "Выберите интересующую вас категорию:",
                reply_markup=keyboard
            )

        await callback.answer()

    except Exception as e:
        logger.error(
            f"Go to main menu error: {e} "
            f"(user: {callback.from_user.id})"
        )
        await callback.answer(
            "❌ Ошибка обработки запроса",
            show_alert=True
        )


@callback_router.callback_query(F.data.startswith("button:"))
async def handle_button_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка callback для кнопок"""
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
                logger.warning(
                    f"Button not found: {callback_data.button_id}"
                )
                await callback.answer(
                    "❌ Кнопка не найдена",
                    show_alert=True
                )
                return

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
            builder = InlineKeyboardBuilder()
            builder.row(
                InlineKeyboardButton(
                    text="Было полезно 👍",
                    callback_data=FeedbackCallback(
                        action="helpful",
                        item_id=callback_data.button_id).pack()
                ),
                InlineKeyboardButton(
                    text="Не помогло 👎",
                    callback_data=FeedbackCallback(
                        action="unhelpful",
                        item_id=callback_data.button_id).pack()
                )
            )
            builder.row(
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data=CategoryCallback(
                        category_id=button.category_id).pack()
                )
            )
            keyboard = builder.as_markup()

            await callback.message.edit_text(
                text,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )

        await callback.answer()

    except Exception as e:
        logger.error(
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

        async with get_session() as session:
            user = await session.get(User, message.from_user.id)
            if not user:
                user = User(
                    telegram_id=message.from_user.id,
                    username=message.from_user.username,
                    is_active=True,
                    is_admin=False
                )
                session.add(user)
                logger.info(f"New user created: {user}")
            elif user.username != message.from_user.username:
                user.username = message.from_user.username
                session.add(user)
                logger.info(
                    f"User {user.telegram_id} "
                    f"updated username to {user.username}"
                )
            new_question = Question(
                text=message.text,
                user_id=user.telegram_id
            )
            session.add(new_question)
            await session.commit()
            await session.refresh(new_question)

            logger.info(
                f"New question #{new_question.id} "
                f"from user {message.from_user.id}"
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
            )
            # Отправляем уведомление всем админам
            for admin_id in ADMINS:
                try:
                    await message.bot.send_message(
                        chat_id=admin_id,
                        text=admin_message,
                        reply_markup=get_admin_answer_keyboard(
                            new_question.id
                        ),
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(
                        "Failed to send question "
                        f"to admin {admin_id}: {e}"
                    )

    except Exception as e:
        logger.error(
            "Error processing question from user "
            f"{message.from_user.id}: {e}"
            )
        await message.answer(
            "❌ Произошла ошибка при отправке вашего вопроса. "
            "Пожалуйста, попробуйте еще раз позже."
        )
        await state.clear()


@callback_router.message(F.text == "🤝 Помощь")
async def help_request(message: Message):
    """Обрабатывает кнопку 'Помощь'."""
    await message.answer(
        "Мы направили в поддержку обращение, "
        "скоро с вами свяжется администратор."
    )
