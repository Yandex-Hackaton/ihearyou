from sqladmin import ModelView
from sqladmin.filters import BooleanFilter

from data.models import User


class UserView(ModelView, model=User):
    name = 'Пользователь'
    name_plural = 'Пользователи'

    # Названия полей
    column_labels = {
        User.telegram_id: 'Telegram ID',
        User.username: 'Никнейм',
        User.is_blocked: 'Доступ в telegram',
        User.is_admin: 'Администратор',
        User.registered_at: 'Дата и время регистрации',
    }

    # Выводимые поля на страницу списка
    column_list = [
        User.username,
        User.is_blocked,
        User.is_admin,
        User.telegram_id,
        User.registered_at,
    ]

    # Выподимые поля на страницу детальной информации
    column_details_list = [
        User.username,
        User.is_blocked,
        User.is_admin,
        User.telegram_id,
        User.registered_at,
    ]
    form_rules = ['is_blocked']
    column_searchable_list = [User.telegram_id]
    column_sortable_list = [User.registered_at, User.is_blocked]
    column_filters = [
        BooleanFilter(User.is_blocked, 'По блокировке'),
    ]
    identity = 'user'
