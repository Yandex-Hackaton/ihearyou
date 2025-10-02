from datetime import datetime
from typing import Any

from aiogram.enums import UpdateType
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import distinct, extract, func, select, text

from data.models import InteractionEvent


class InteractionEventService:
    """Сервисы для взаимодействия с `InteractionEventModel`."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_event(self, event: InteractionEvent) -> None:
        """Создание записи InteractionEvent в бд."""
        self.db.add(event)
        await self.db.commit()

    async def count_unique_users(self) -> int:
        """Количество уникальных пользователей."""
        query = select(func.count(distinct(InteractionEvent.user_id)))
        result = await self.db.execute(query)
        count = result.scalar()
        return count or 0

    async def count_total_events(self) -> int:
        """Общее количество событий."""
        query = select(func.count(InteractionEvent.id))
        result = await self.db.execute(query)
        count = result.scalar()
        return count or 0

    async def get_average_events_per_user(self) -> int:
        """Среднее количество событий на пользователя."""
        total = await self.count_total_events()
        unique = await self.count_unique_users()
        if unique == 0:
            return 0
        return total // unique

    async def get_monthly_event_counts(
        self,
        year: int = datetime.now().year,
    ) -> list[dict[str, Any]]:
        """Количество событий по месяцам для указанного или текущего года.

        Пример вывода:
            ```python
            [{'month': datetime.datetime(2025, 7, 1, 0, 0), 'count': 2},
             {'month': datetime.datetime(2025, 8, 1, 0, 0), 'count': 2},
             {'month': datetime.datetime(2025, 9, 1, 0, 0), 'count': 41}]
             ```
        """
        # date_trunc это функция PostgreSQL округляет дату вниз до начала месяца
        # 2025-09-17 12:34 → 2025-09-01 00:00
        truncated = func.date_trunc("month", InteractionEvent.created_at).label("month")
        query = (
            select(truncated, func.count(InteractionEvent.id).label("count"))
            .where(extract("year", InteractionEvent.created_at) == year)
            .group_by(truncated)
            .order_by(truncated)
        )
        result = await self.db.execute(query)
        rows = result.all()
        return [{"month": row.month, "count": row.count} for row in rows]

    async def get_event_count_last_week(
        self,
    ) -> list[dict[str, datetime | int]]:
        """Активность пользователей за последнюю неделю.

        Пример вывода:
            ```python
            [{'day': datetime.datetime(2025, 9, 25, 0, 0), 'count': 10},
            {'day': datetime.datetime(2025, 9, 26, 0, 0), 'count': 20},
            {'day': datetime.datetime(2025, 9, 27, 0, 0), 'count': 30}]
            ```
        """
        truncated = func.date_trunc("day", InteractionEvent.created_at).label("day")
        query = (
            select(truncated, func.count(InteractionEvent.id).label("count"))
            .where(
                InteractionEvent.created_at >= func.now() - text("interval '7 days'")
            )
            .group_by(truncated)
            .order_by(truncated)
        )
        result = await self.db.execute(query)
        rows = result.all()
        result_list = [{"day": row.day, "count": row.count} for row in rows]
        return result_list

    async def get_users_with_only_one_message_count(self) -> int:
        """Количество пользователей, которые не пошли дальше /start."""
        subquery = (
            select(InteractionEvent.user_id)
            .group_by(InteractionEvent.user_id)  # type: ignore[attr-defined]
            .having(func.count(InteractionEvent.id) == 1)
        ).subquery()
        query = (
            select(func.count(distinct(InteractionEvent.user_id)))
            .where(InteractionEvent.message_text == "/start")
            .where(InteractionEvent.user_id.in_(subquery))  # type: ignore[attr-defined]
        )
        result = await self.db.execute(query)
        count = result.scalar()
        return count or 0

    async def get_most_popular_messages(self) -> list[dict[str, Any]]:
        """Топ-10 самых популярных сообщений пользователей.

        Пример вывода: `[{"message": "/start", "count": 50}, {"message": "help", "count": 20}]`.
        """
        query = (
            select(
                InteractionEvent.message_text,
                func.count(InteractionEvent.id).label("count"),
            )
            .where(InteractionEvent.event_type == UpdateType.MESSAGE)
            .where(InteractionEvent.message_text.isnot(None))  # type: ignore
            .group_by(InteractionEvent.message_text)
            .order_by(func.count(InteractionEvent.id).desc())
            .limit(10)
        )
        result = await self.db.execute(query)
        rows = result.all()
        return [{"message": row.message_text, "count": row.count} for row in rows]

    async def get_most_popular_callbacks(self) -> list[dict[str, Any]]:
        """Топ-10 самых популярных callback кнопок.

        Пример вывода: [{"callback": "button1", "count": 30}, {"callback": "help", "count": 15}].
        """
        query = (
            select(
                InteractionEvent.callback_data,
                func.count(InteractionEvent.id).label("count"),
            )
            .where(InteractionEvent.event_type == UpdateType.CALLBACK_QUERY)
            .where(InteractionEvent.callback_data.isnot(None))  # type: ignore
            .group_by(InteractionEvent.callback_data)
            .order_by(func.count(InteractionEvent.id).desc())
            .limit(10)
        )
        result = await self.db.execute(query)
        rows = result.all()
        return [{"callback": row.callback_data, "count": row.count} for row in rows]

    async def get_callback_usage_count(self, callback_data: str) -> int:
        """Количество использований колбэка по имени."""
        query = select(func.count(InteractionEvent.id)).where(
            InteractionEvent.callback_data == callback_data
        )
        result = await self.db.execute(query)
        count = result.scalar()
        return count or 0
