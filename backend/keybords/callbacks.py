from aiogram.fsm.state import State, StatesGroup
from pydantic import BaseModel


class MainMenuCallback(BaseModel):
    """Callback для главного меню"""
    category_id: int
    
    def pack(self) -> str:
        return f"main_menu:{self.category_id}"
    
    @classmethod
    def unpack(cls, data: str) -> 'MainMenuCallback':
        category_id = int(data.split(":")[1])
        return cls(category_id=category_id)


class CategoryCallback(BaseModel):
    """Callback для категорий"""
    category_id: int


class ButtonCallback(BaseModel):
    """Callback для кнопок"""
    button_id: int
    
    def pack(self) -> str:
        return f"button:{self.button_id}"
    
    @classmethod
    def unpack(cls, data: str) -> 'ButtonCallback':
        button_id = int(data.split(":")[1])
        return cls(button_id=button_id)


class UserStates(StatesGroup):
    """Состояния пользователя"""
    MAIN_MENU = State()
    CATEGORY_VIEW = State()
    BUTTON_CONTENT = State()