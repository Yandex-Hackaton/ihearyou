from data.db import get_session
from data.models import InteractionEvent


class InteractionEventService:
    """Сервисы для взаимодействия с InteractionEvent."""

    @staticmethod
    async def save_event(event: InteractionEvent):
        """Сохранение события в БД."""
        async with get_session() as session:
            session.add(event)
            # commit происходит автоматически
            # в контекстном менеджере get_session
