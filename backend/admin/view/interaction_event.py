from admin.base import CustomModelView
from data.models import InteractionEvent


class InteractionEventView(CustomModelView, model=InteractionEvent):
    """Представление для событий взаимодействия с ботом."""

    name = "Событие"
    name_plural = "События взаимодействий"
    icon = "fa-solid fa-chart-line"

    # Права доступа - только чтение
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True

    # Названия полей
    column_labels = {
        InteractionEvent.id: "ID",
        InteractionEvent.event_type: "Тип события",
        InteractionEvent.user_id: "ID пользователя",
        InteractionEvent.message_text: "Текст сообщения",
        InteractionEvent.callback_data: "Данные кнопки",
        InteractionEvent.created_at: "Дата и время",
    }

    # Список колонок для отображения
    column_list = [
        InteractionEvent.created_at,
        InteractionEvent.event_type,
        InteractionEvent.user_id,
        InteractionEvent.message_text,
        InteractionEvent.callback_data,
    ]

    # Детальная информация
    column_details_list = [
        InteractionEvent.id,
        InteractionEvent.event_type,
        InteractionEvent.user_id,
        InteractionEvent.message_text,
        InteractionEvent.callback_data,
        InteractionEvent.created_at,
    ]

    # Поля для поиска
    column_searchable_list = [
        InteractionEvent.message_text,
        InteractionEvent.callback_data,
    ]

    # Сортировка
    column_sortable_list = [
        InteractionEvent.created_at,
        InteractionEvent.event_type,
        InteractionEvent.user_id,
    ]

    # Фильтры (отключены из-за конфликта типов с SQLAdmin)
    # Используйте поиск и сортировку вместо фильтров
    column_filters = []

    # Количество записей на странице
    page_size = 50
    page_size_options = [25, 50, 100, 200]

    # Сортировка по умолчанию (новые сверху)
    column_default_sort = [(InteractionEvent.created_at, True)]

    # Форматирование колонок
    @staticmethod
    def format_datetime(model, attribute):
        """Форматирование даты и времени."""
        return model.created_at.strftime("%d.%m.%Y %H:%M:%S")

    @staticmethod
    def format_user(model, attribute):
        """Форматирование пользователя."""
        return f"ID: {model.user_id}"

    @staticmethod
    def format_message(model, attribute):
        """Форматирование текста сообщения."""
        if not model.message_text:
            return "—"
        # Ограничиваем длину для отображения в списке
        if len(model.message_text) > 50:
            return model.message_text[:47] + "..."
        return model.message_text

    @staticmethod
    def format_callback(model, attribute):
        """Форматирование callback данных."""
        if not model.callback_data:
            return "—"
        return model.callback_data

    column_formatters = {
        InteractionEvent.created_at: format_datetime,
        InteractionEvent.message_text: format_message,
        InteractionEvent.callback_data: format_callback,
    }

    column_formatters_detail = {
        InteractionEvent.created_at: format_datetime,
    }

    # Дополнительная статистика (можно добавить в будущем)
    async def get_count_query(self, request):
        """Получить запрос для подсчета общего количества."""
        return await super().get_count_query(request)
