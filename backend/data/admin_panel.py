from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqladmin.filters import ForeignKeyFilter
from passlib.context import CryptContext

from .models import User, Button, Category, Role
from .db import engine, create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(
    title="IHearYou Admin Panel", 
    version="1.0.0",
    lifespan=lifespan
)

admin = Admin(app, engine, title="Управление IHearYou Ботом")

class UserAdmin(ModelView, model=User):
    name = 'Пользователь'
    name_plural = 'Пользователи'
    column_list = (
        User.id,
        User.username,
        'full_name',
        User.birth_date,
        User.role_id,
    )
    column_labels = {
        User.id: 'Идентификатор',
        User.name: 'Имя',
        User.username: 'Никнейм',
        User.surname: 'Фамилия',
        User.patronymic: 'Отчество',
        User.password: 'Пароль',
        User.birth_date: 'Дата рождения',
        User.role: 'Роль',
        User.role_id: 'Роль',
        'full_name': 'Полное имя',
    }
    column_searchable_list = [User.username, User.name, User.surname]
    column_sortable_list = [User.id, User.username, User.birth_date]
    form_edit_rules = [
        'name',
        'surname',
        'patronymic',
        'birth_date',
        'role',
    ]
    icon = 'fa-solid fa-user'

    async def on_model_change(self, data, model, is_created, request) -> None:
        if is_created:
            pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
            data['password'] = pwd_context.hash(data['password'])

class ButtonAdmin(ModelView, model=Button):
    name = 'Кнопка'
    name_plural = 'Кнопки'
    column_exclude_list = [Button.category]
    column_filters = [
        ForeignKeyFilter(
            Button.category_id,
            Category.title,
            title='По категории',
        ),
    ]
    column_labels = {
        Button.id: 'Идентификатор',
        Button.title: 'Название',
        Button.description: 'Описание',
        Button.category: 'Категория',
        Button.category_id: 'Категория',
        Button.content: 'Контент',
    }
    column_searchable_list = [Button.title, Button.category]
    column_sortable_list = [Button.title, Button.category]

class CategoryAdmin(ModelView, model=Category):
    name = 'Категория'
    name_plural = 'Категории'
    column_exclude_list = [Category.for_user_role, Category.buttons]
    column_labels = {
        Category.id: 'Идентификатор',
        Category.slug: 'Короткое название',
        Category.title: 'Название',
        Category.description: 'Описание',
        Category.for_user_role: 'Предназначена для',
        Category.for_user_role_id: 'Предназначена для',
        Category.buttons: 'Кнопки',
    }
    column_searchable_list = [Category.slug, Category.title]
    column_sortable_list = [
        Category.slug,
        Category.title,
        Category.for_user_role,
    ]

class RoleAdmin(ModelView, model=Role):
    name = 'Роль'
    name_plural = 'Роли'
    column_exclude_list = [Role.users, Role.categories]
    column_labels = {
        Role.id: 'Идентификатор',
        Role.slug: 'Короткое название',
        Role.title: 'Название',
        Role.description: 'Описание',
        Role.users: 'Пользователи',
        Role.categories: 'Категории',
    }
    column_searchable_list = [Role.slug, Role.title]
    column_sortable_list = [Role.title, Role.slug, Role.categories]

admin.add_view(UserAdmin)
admin.add_view(ButtonAdmin)
admin.add_view(CategoryAdmin)
admin.add_view(RoleAdmin)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)