from sqladmin import ModelView

from data.models import Category


class CategoryView(ModelView, model=Category):
    name = 'Категория'
    name_plural = 'Категории'

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
        Category.is_active
    ]
    # Поля страницы с детальной информацией
    column_details_list = [
        Category.id,
        Category.title,
        Category.description,
        Category.is_active,
        Category.created_at,
    ]

    # Поля доступные для создания и редактирования
    form_rules = [
        'title',
        'description',
        'is_active',
    ]
