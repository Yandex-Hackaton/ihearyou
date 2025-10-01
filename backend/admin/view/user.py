from sqladmin.filters import BooleanFilter

from data.models import User
from admin.base import CustomModelView


class UserView(CustomModelView, model=User):
    name = 'Пользователь'
    name_plural = 'Пользователи'
    icon = "fa-solid fa-users"

    # Разрешённые действия с моделью
    can_create = False
    can_edit = True
    can_delete = False

    # Названия полей
    column_labels = {
        User.telegram_id: 'Telegram ID',
        User.username: 'Никнейм',
        User.is_active: 'Доступен',
        User.is_admin: 'Админ',
        User.registered_at: 'Дата и время регистрации',
    }

    # Выводимые поля на страницу списка
    column_list = [
        User.username,
        User.is_admin,
        User.telegram_id,
        User.is_active,
        User.registered_at,
    ]

    # Выводимые поля на страницу детальной информации
    column_details_list = [
        User.username,
        User.is_active,
        User.is_admin,
        User.telegram_id,
        User.registered_at,
    ]

    # Поля доступные для изменений
    form_columns = ['is_active']
    column_sortable_list = [User.registered_at, User.is_active]
    column_filters = [
        BooleanFilter(User.is_active, 'Доступен'),
    ]
    identity = 'user'

    @staticmethod
    def format_datetime(model, attribute):
        return model.registered_at.strftime("%d.%m.%Y %H:%M")

    column_formatters = {
        User.registered_at: format_datetime
    }

    column_formatters_detail = {
        User.registered_at: format_datetime
    }
