from sqladmin import ModelView

from data.models import Content


class ContentView(ModelView, model=Content):
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
        Content.description,
        Content.is_active,
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

    form_rules = [
        'title',
        'description',
        'url_link',
        'is_active',
        'category',
    ]
