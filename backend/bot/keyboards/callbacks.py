from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup


class CategoryCallback(CallbackData, prefix="category"):
    """Callback для выбора категории"""
    category_id: int


class ButtonCallback(CallbackData, prefix="button"):
    """Callback для нажатия на конкретную кнопку (внутри категории)"""
    button_id: int


class GoToMainMenuCallback(CallbackData, prefix="go_main"):
    """Callback для возврата в главное меню"""
    pass


class MainMenuCallback(CallbackData, prefix="main_menu"):
    """Callback для возврата в главное меню с указанием категории"""
    category_id: int


class UserStates(StatesGroup):
    """Состояния пользователя"""
    MAIN_MENU = State()
    CATEGORY_VIEW = State()
    BUTTON_CONTENT = State()

