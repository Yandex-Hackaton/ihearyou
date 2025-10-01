from data.models import Category
from admin.base import CustomModelView


class CategoryView(CustomModelView, model=Category):
    name = 'Категория'
    name_plural = 'Категории'
    icon = "fa-solid fa-folder"

    # Названия полей
    column_labels = {
        Category.id: 'ID',
        Category.title: 'Название',
        Category.description: 'Краткое описание',
        Category.is_active: 'Активна',
        Category.created_at: 'Дата и время создания',
    }

    # Поля страницы списка
    column_list = [
        Category.id,
        Category.title,
        Category.is_active,
        Category.created_at,
    ]
    # Поля страницы с детальной информацией
    column_details_list = [
        Category.id,
        Category.title,
        Category.description,
        Category.is_active,
        Category.created_at,
    ]

    # Поля доступные для изменений
    form_columns = [
        Category.title,
        Category.description,
        Category.is_active,
    ]

    @staticmethod
    def format_datetime(model, attribute):
        return model.created_at.strftime("%d.%m.%Y %H:%M")

    column_formatters = {
        Category.created_at: format_datetime
    }

    column_formatters_detail = {
        Category.created_at: format_datetime
    }
