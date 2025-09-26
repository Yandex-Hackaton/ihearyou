from sqladmin import ModelView

from stats.models import InteractionEvent


class InteractionEventAdmin(ModelView, model=InteractionEvent):
    column_list = [
        "id",
        "event_type",
        "user_id",
        "username",
        "message_text",
        "callback_data",
        "created_at",
    ]
    column_searchable_list = ["username", "message_text", "callback_data"]
    column_sortable_list = ["id", "created_at"]
