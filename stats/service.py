from core.db import async_session
from stats.models import InteractionEvent


class InteractionEventService:
    """Сервисы для взаимодействия с InteractionEventModel"""

    @staticmethod
    async def save_event(event: InteractionEvent):
        async with async_session() as db:
            db.add(event)
            await db.commit()
