from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from ..keyboards.callbacks import (
    MainMenuCallback,
    ButtonCallback,
    UserStates,
    CategoryCallback,
)
from ..keyboards.main_menu import get_category_buttons_keyboard, get_main_menu_keyboard
from data.queries import get_category_by_id, get_button_by_id
from data.db import get_session
from utils.logger import logger

callback_router = Router()


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
            category = await get_category_by_id(callback_data.category_id, session)

            if not category:
                logger.warning(f"Category not found: {callback_data.category_id}")
                await callback.answer("❌ Категория не найдена", show_alert=True)
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
        logger.error(
            f"Category callback error: {e} " f"(user: {callback.from_user.id})"
        )
        await callback.answer("❌ Ошибка обработки запроса", show_alert=True)


@callback_router.callback_query(F.data.startswith("main_menu:"))
async def handle_main_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка callback для главного меню"""
    try:
        callback_data = MainMenuCallback.unpack(callback.data)

        if callback_data.category_id == 0:
            # Return to main menu
            logger.info(f"Return to main menu: {callback.from_user.id}")
            await state.set_state(UserStates.MAIN_MENU)

            async with get_session() as session:
                keyboard = await get_main_menu_keyboard(session)
                await callback.message.edit_text(
                    "🏠 Главное меню\n\n" "Выберите интересующую вас категорию:",
                    reply_markup=keyboard,
                )

        else:
            await state.set_state(UserStates.CATEGORY_VIEW)

            async with get_session() as session:
                category = await get_category_by_id(callback_data.category_id, session)

                if not category:
                    logger.warning(
                        f"Category not found in main menu: "
                        f"{callback_data.category_id}"
                    )
                    await callback.answer("❌ Категория не найдена", show_alert=True)
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
        logger.error(
            f"Main menu callback error: {e} " f"(user: {callback.from_user.id})"
        )
        await callback.answer("❌ Ошибка обработки запроса", show_alert=True)


@callback_router.callback_query(F.data == "go_main")
async def handle_go_to_main_menu_callback(callback: CallbackQuery, state: FSMContext):
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
        logger.error(f"Go to main menu error: {e} " f"(user: {callback.from_user.id})")
        await callback.answer("❌ Ошибка обработки запроса", show_alert=True)


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
                logger.warning(f"Button not found: {callback_data.button_id}")
                await callback.answer("❌ Кнопка не найдена", show_alert=True)
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

            # Create keyboard with "Back" button
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🔙 Назад",
                            callback_data=CategoryCallback(
                                category_id=button.category_id
                            ).pack(),
                        )
                    ]
                ]
            )

            await callback.message.edit_text(text, reply_markup=keyboard)

        await callback.answer()

    except Exception as e:
        logger.error(f"Button callback error: {e} " f"(user: {callback.from_user.id})")
        await callback.answer("❌ Ошибка обработки запроса", show_alert=True)
