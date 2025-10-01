from datetime import datetime, timedelta
from sqlmodel import select, func
from aiogram import Bot

from data.models import User, InteractionEvent
from data.db import get_session
from utils.logger import logger


class ReminderService:
    """Сервис для отправки напоминаний неактивным пользователям."""

    @staticmethod
    async def get_inactive_users(days: int = 7) -> list[User]:
        cutoff_date = datetime.now() - timedelta(days=days)

        async with get_session() as session:
            # Подзапрос для получения последней активности каждого пользователя
            last_activity_subquery = (
                select(
                    InteractionEvent.user_id,
                    func.max(InteractionEvent.created_at).label('last_activity')
                )
                .where(InteractionEvent.user_id.isnot(None))
                .group_by(InteractionEvent.user_id)
                .subquery()
            )

            # Основной запрос для получения неактивных пользователей
            query = (
                select(User)
                .outerjoin(
                    last_activity_subquery,
                    User.telegram_id == last_activity_subquery.c.user_id
                )
                .where(
                    (last_activity_subquery.c.last_activity < cutoff_date) |
                    (last_activity_subquery.c.last_activity.is_(None))
                )
                .where(User.is_active is True)
            )

            result = await session.execute(query)
            inactive_users = result.scalars().all()

            logger.info(f"Найдено {len(inactive_users)} неактивных пользователей")
            return inactive_users

    @staticmethod
    async def send_reminders_to_inactive_users(
        bot: Bot,
        reminder_text: str,
        days: int = 7
    ) -> dict:
        inactive_users = await ReminderService.get_inactive_users(days)

        results = {
            'total': len(inactive_users),
            'sent': 0,
            'failed': 0,
            'errors': []
        }

        for user in inactive_users:
            try:
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=reminder_text,
                    disable_web_page_preview=True
                )
                results['sent'] += 1
                logger.info(
                    f"Напоминание отправлено для {user.telegram_id}"
                )

            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"User {user.telegram_id}: {str(e)}")
                logger.error(
                    f"Ошибка отправки напоминания для {user.telegram_id}: {e}"
                )

        logger.info(
            f"Напоминания отправлены: {results['sent']}/{results['total']}, "
            f"ошибок: {results['failed']}"
        )

        return results
