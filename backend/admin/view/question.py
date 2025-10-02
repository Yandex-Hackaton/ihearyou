import logging

from sqlalchemy.orm import selectinload
from starlette.requests import Request

from admin.base import CustomModelView
from data.models import Question

logger = logging.getLogger(__name__)


class QuestionView(CustomModelView, model=Question):
    name = "Вопрос"
    name_plural = "Вопросы"
    icon = "fa-solid fa-circle-question"

    # Разрешённые действия с моделью
    can_create = False
    can_edit = True
    can_delete = False

    # Название полей
    column_labels = {
        Question.id: "ID",
        Question.text: "Вопрос",
        Question.user: "Пользователь",
        Question.created_at: "Дата и время получения вопроса",
    }

    # Поля страницы списка
    column_list = [
        Question.id,
        Question.text,
        Question.created_at,
        Question.user,
    ]

    # Поля на странице детальной информации
    column_details_list = [
        Question.id,
        Question.text,
        Question.answer_text,
        Question.created_at,
        Question.user,
    ]

    # Поля доступные для изменений
    form_columns = [
        "answer",
    ]

    def list_query(self, request: Request):
        return super().list_query(request).options(selectinload(Question.user))

    def details_query(self, request: Request):
        return super().details_query(request).options(
            selectinload(Question.user)
        )

    @staticmethod
    def format_user(model: Question, attribute) -> str:
        return model.user.telegram_id if model.user else "Неизвестно"

    @staticmethod
    def format_datetime(model: Question, attribute) -> str:
        return model.created_at.strftime("%d.%m.%Y %H:%M")

    column_formatters = {
        Question.user: format_user,
        Question.created_at: format_datetime,
    }

    column_formatters_detail = {
        Question.user: format_user,
        Question.created_at: format_datetime,
    }

    async def on_model_change(self, data, model, is_created, request):
        """Специальное логирование для ответов на вопросы"""
        model_name = self._get_model_name()
        model_id = self._get_model_id(model)

        if is_created:
            logger.info(f"Admin created {model_name} (ID: {model_id})")
        else:
            # Проверяем, был ли добавлен ответ
            if hasattr(model, "answer") and model.answer:
                logger.info(f"Admin answered {model_name} (ID: {model_id})")
            else:
                logger.info(f"Admin updated {model_name} (ID: {model_id})")
