from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqladmin.filters import BooleanFilter, ForeignKeyFilter

from .models import User, Category, Content, Question
from .db import engine, create_db_and_tables, load_fixtures


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    await load_fixtures('initial_data.json')
    yield

app = FastAPI(
    title="IHearYou Admin Panel",
    version="1.0.0",
    lifespan=lifespan,
)

admin = Admin(app, engine, title="IHearYou Admin")


class UserAdmin(ModelView, model=User):
    name = 'Пользователь'
    name_plural = 'Пользователи'
    column_list = (
        User.telegram_id,
        User.is_blocked,
        User.registered_at,
    )
    column_labels = {
        User.telegram_id: 'Идентификатор (Telegram ID)',
        User.username: 'Никнейм',
        User.password: 'Пароль',
        User.is_blocked: 'Статус блокировки',
        User.is_admin: 'Статус администратора',
        User.registered_at: 'Дата и время регистрации',
    }
    form_rules = ['is_blocked']  # админ может только блокировать пользователей
    column_searchable_list = [User.telegram_id]
    column_sortable_list = [User.registered_at, User.is_blocked]
    column_filters = [
        BooleanFilter(User.is_blocked, 'По блокировке'),
    ]
    can_create = True  # после деплоя на сервер, переключить на значение False
    identity = 'user'


class ContentAdmin(ModelView, model=Content):
    name = 'Контент'
    name_plural = 'Контенты'
    column_exclude_list = [
        Content.image_path,
        Content.url_link,
        Content.category_id,
        Content.category,
    ]
    column_labels = {
        Content.id: 'Идентификатор',
        Content.title: 'Текст кнопки',
        Content.description: 'Краткое описание',
        Content.image_path: 'Изображение',
        Content.url_link: 'Ссылка к основному тексту',
        Content.is_active: 'Статус активности',
        Content.category: 'Категория',
        Content.category_id: 'Категория',
        Content.created_at: 'Дата и время создания',
    }
    column_searchable_list = [Content.title, Content.description]
    column_sortable_list = [
        Content.title,
        Content.created_at,
        Content.is_active,
    ]
    form_rules = [
        'title',
        'description',
        'text',
        'image_path',
        'url_link',
        'is_active',
        'category',
    ]
    column_filters = [
        BooleanFilter(Content.is_active, 'По активности'),
        ForeignKeyFilter(
            Content.category_id,
            Category.title,
            title='По категориям'
        ),
    ]


class CategoryAdmin(ModelView, model=Category):
    name = 'Категория'
    name_plural = 'Категории'
    column_exclude_list = [Category.contents]
    column_labels = {
        Category.id: 'Идентификатор',
        Category.title: 'Название кнопки',
        Category.description: 'Краткое описание',
        Category.is_active: 'Статус активности',
        Category.created_at: 'Дата и время создания',
    }
    form_rules = [
        'title',
        'description',
        'is_active',
    ]
    column_searchable_list = [Category.title, Category.description]
    column_sortable_list = [
        Category.title,
        Category.is_active,
        Category.created_at,
    ]
    column_filters = [
        BooleanFilter(Category.is_active, 'По активности'),
    ]


class QuestionAdmin(ModelView, model=Question):
    name = 'Запрос от пользователя'
    name_plural = 'Запросы от пользователей'
    column_exclude_list = [Question.user_id]
    column_labels = {
        Question.id: 'Идентификатор',
        Question.text: 'Текст',
        Question.user_id: 'Пользователь',
        Question.created_at: 'Дата и время создания запроса',
        Question.user: 'Пользователь',
        Question.answer: 'Ответ',
    }
    form_rules = [
        'text',
        'user',
    ]
    column_searchable_list = [Question.text, Question.user_id]
    column_sortable_list = [Question.created_at]
    can_create = True  # после деплоя на сервер, переключить на значение False
    can_edit = False
    can_delete = True


admin.add_view(UserAdmin)
admin.add_view(CategoryAdmin)
admin.add_view(ContentAdmin)
admin.add_view(QuestionAdmin)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
