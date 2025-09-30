from starlette.requests import Request
from sqladmin import ModelView
from sqlalchemy.orm import selectinload

from data.models import Question


class QuestionView(ModelView, model=Question):
    name = 'Вопрос'
    name_plural = 'Вопросы'
    # Запрещаем действия с этой моделью
    can_create = False
    can_edit = True
    can_delete = False

    # Название полей
    column_labels = {
        Question.id: 'ID',
        Question.text: 'Вопрос',
        Question.user: 'Пользователь',
        Question.created_at: 'Дата и время получения вопроса',
    }

    # Поля страницы списка
    column_list = [
        Question.id,
        Question.text,
        Question.created_at,
        Question.user,
    ]
    form_rules = [
        'answer',
    ]

    def list_query(self, request: Request):
        return (
            super().list_query(request)
            .options(selectinload(Question.user))
        )

    column_formatters = {
        Question.user: lambda m, a: m.user.username if m.user else "Неизвестно",
        Question.created_at: lambda m, a: m.created_at.strftime("%d.%m.%Y %H:%M")
    }
