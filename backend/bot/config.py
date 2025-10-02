import logging
from typing import List
from decouple import config

logger = logging.getLogger(__name__)

# Основные настройки
BOT_TOKEN = config('BOT_TOKEN')
ADMINS: List[int] = list(map(int, config('ADMINS').split()))


# Тексты сообщений
class Messages:
    """Тексты сообщений бота."""
    
    # Приветствие
    WELCOME_USER = (
        "Для удобной навигации, выберите подходящую тему.\n"
        "Если не найдёшь подходящую, можешь задать вопрос, "
        "а мы поможем с ответом)"
    )
    
    WELCOME_ADMIN = (
        "👋 Добро пожаловать, администратор!\n\n"
        "Используйте кнопки ниже для управления ботом."
    )
    
    # Ошибки
    CATEGORY_NOT_FOUND = "❌ Категория не найдена"
    BUTTON_NOT_FOUND = "❌ Кнопка не найдена"
    CONTENT_NOT_FOUND = "❌ Контент не найден"
    PROCESSING_ERROR = "❌ Ошибка обработки запроса"
    
    # Вопросы
    QUESTION_PROMPT = (
        "Не нашли нужную информацию? "
        "Напишите свой вопрос, и мы передадим его администратору. "
        "В ближайшее время вы получите ответ."
    )
    
    QUESTION_SENT = (
        "✅ Спасибо! Ваш вопрос отправлен администратору. "
        "Мы сообщим вам, как только поступит ответ."
    )
    
    # Обратная связь
    FEEDBACK_HELPFUL = (
        "Мы рады, что смогли вам помочь! 😊\n\n"
        "Пожалуйста, оцените материал."
    )
    FEEDBACK_UNHELPFUL = (
        "Спасибо за обратную связь! "
        "Мы постараемся улучшить материал. 🙏"
    )
    RATING_THANKS = "Спасибо за оценку! ⭐"


# Настройки напоминаний
class ReminderSettings:
    """Настройки системы напоминаний."""
    
    INACTIVE_DAYS = 7  # Дней неактивности для отправки напоминания
    
    # Импортируем тексты напоминаний из urls.py
    from bot.urls import URLBuilder
    TEXTS = URLBuilder.get_reminder_texts()


# Настройки изображений
class ImageSettings:
    """Настройки для работы с изображениями."""
    
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
    ALLOWED_FORMATS = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    FALLBACK_ENABLED = True  # Включить fallback логику