from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup
from typing import Optional


class CategoryCallback(CallbackData, prefix="category"):
    """Callback для выбора категории"""

    category_id: int


class ButtonCallback(CallbackData, prefix="button"):
    """Callback для нажатия на конкретную кнопку (внутри категории)"""

    button_id: int


class GoToMainMenuCallback(CallbackData, prefix="go_main"):
    """Callback для возврата в главное меню"""

    pass


class AdminCallback(CallbackData, prefix="admin"):
    action: str
    question_id: Optional[int] = None
    reminder_type: Optional[str] = None


class AdminCategoryCallback(CallbackData, prefix="admin_category"):
    """Callback для выбора категории админом"""
    category_id: int


class AdminContentCallback(CallbackData, prefix="admin_content"):
    """Callback для выбора контента админом"""
    content_id: int


class AdminContentActionCallback(CallbackData, prefix="admin_action"):
    """Callback для действий с контентом"""
    action: str
    content_id: int


class FeedbackCallback(CallbackData, prefix="feedback"):
    action: str
    content_id: int


class RatingCallback(CallbackData, prefix="rating"):
    rating: int
    content_id: int


class UserStates(StatesGroup):
    """Состояния пользователя"""

    MAIN_MENU = State()
    CATEGORY_VIEW = State()
    BUTTON_CONTENT = State()
    QUESTION = State()  # Состояние ожидания вопроса от пользователя
    ANSWER = State()   # Состояние ожидания ответа от админа
    REVIEW = State()   # Состояние ожидания оценки (1-5)
    UPLOADING_IMAGE = State()  # Состояние загрузки изображения
    
    # Админские состояния
    ADMIN_CATEGORY_VIEW = State()  # Админ просматривает категории
    ADMIN_CONTENT_VIEW = State()  # Админ просматривает контент категории
    ADMIN_CONTENT_MANAGE = State()  # Админ управляет контентом
