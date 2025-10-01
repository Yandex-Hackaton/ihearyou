from starlette.requests import Request
from sqlalchemy.orm import selectinload

from data.models import Content
from admin.base import CustomModelView


class ContentView(CustomModelView, model=Content):
    name = 'Контент'
    name_plural = 'Контенты'

    # Названия полей
    column_labels = {
        Content.id: 'ID',
        Content.title: 'Название',
        Content.description: 'Краткое описание',
        Content.url_link: 'Ссылка',
        Content.is_active: 'Активно',
        Content.category: 'Категория',
        Content.created_at: 'Дата и время создания',
    }

    # Поля на странице списка
    column_list = [
        Content.id,
        Content.title,
        Content.category,
        Content.is_active,
        Content.created_at,
    ]

    # Поля на странице детальной информации
    column_details_list = [
        Content.id,
        Content.title,
        Content.description,
        Content.url_link,
        Content.is_active,
        Content.category,
        Content.created_at,
    ]

    # Поля доступные для изменений
    form_columns = [
        Content.title,
        Content.description,
        Content.url_link,
        Content.is_active,
        Content.category,
    ]

    def list_query(self, request: Request):
        return (
            super().list_query(request)
            .options(selectinload(Content.category))
        )

    def details_query(self, request: Request):
        return (
            super().details_query(request)
            .options(selectinload(Content.category))
        )

    @staticmethod
    def format_category(model, attribute):
        return model.category.title if model.category else "Без категории"

    @staticmethod
    def format_datetime(model, attribute):
        return model.created_at.strftime("%d.%m.%Y %H:%M")

    column_formatters = {
        Content.category: format_category,
        Content.created_at: format_datetime
    }

    column_formatters_detail = {
        Content.category: format_category,
        Content.created_at: format_datetime
    }
