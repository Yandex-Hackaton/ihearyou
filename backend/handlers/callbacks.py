from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from keybords.callbacks import MainMenuCallback, ButtonCallback, UserStates
from keybords.main_menu import get_main_menu_keyboard, get_category_buttons_keyboard
from db_handler.queries import get_category_by_id, get_button_by_id
from data.db import get_session

callback_router = Router()


@callback_router.callback_query(F.data.startswith("main_menu:"))
async def handle_main_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка callback для главного меню"""
    try:
        callback_data = MainMenuCallback.unpack(callback.data)
        
        if callback_data.category_id == 0:
            # Return to main menu
            await state.set_state(UserStates.MAIN_MENU)
            
            async for session in get_session():
                keyboard = await get_main_menu_keyboard(session)
                await callback.message.edit_text(
                    "🏠 Главное меню\n\nВыберите интересующую вас категорию:",
                    reply_markup=keyboard
                )
                break
        else:
            await state.set_state(UserStates.CATEGORY_VIEW)
            
            async for session in get_session():
                category = await get_category_by_id(callback_data.category_id, session)
                
                if not category:
                    await callback.answer("❌ Категория не найдена", show_alert=True)
                    return
                
                keyboard = await get_category_buttons_keyboard(callback_data.category_id, session)
                
                await callback.message.edit_text(
                    f"📂 {category.title}\n\n{category.description or 'Выберите интересующий вас раздел:'}",
                    reply_markup=keyboard
                )
                break
        
        await callback.answer()
        
    except Exception as e:
        await callback.answer("❌ Ошибка обработки запроса", show_alert=True)
        print(f"Error in main menu callback: {e}")


@callback_router.callback_query(F.data.startswith("button:"))
async def handle_button_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка callback для кнопок"""
    try:
        callback_data = ButtonCallback.unpack(callback.data)
        await state.set_state(UserStates.BUTTON_CONTENT)
        
        async for session in get_session():
            button = await get_button_by_id(callback_data.button_id, session)
            
            if not button:
                await callback.answer("❌ Кнопка не найдена", show_alert=True)
                return
            
            text = f"📌 {button.title}\n\n"
            
            if button.description:
                text += f"📝 {button.description}\n\n"
            
            if button.content:
                text += f"📄 {button.content}"
            else:
                text += "ℹ️ Информация по данному разделу будет добавлена в ближайшее время."
            
            # Create keyboard with "Back" button
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data=MainMenuCallback(category_id=button.category_id).pack())]
            ])
            
            await callback.message.edit_text(
                text,
                reply_markup=keyboard
            )
            break
        
        await callback.answer()
        
    except Exception as e:
        await callback.answer("❌ Ошибка обработки запроса", show_alert=True)
        print(f"Error in button callback: {e}")