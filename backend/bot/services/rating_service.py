from logging import getLogger
from sqlalchemy import select

from data.db import get_session
from data.models import Rating

logger = getLogger(__name__)


class RatingService:
    """Сервис для работы с рейтингами."""

    @staticmethod
    async def get_or_create_rating(user_id: int, content_id: int, session) -> Rating:
        """Получает существующий рейтинг или создает новый."""
        existing_rating = await session.execute(
            select(Rating).where(
                Rating.user_id == user_id,
                Rating.content_id == content_id
            )
        )
        rating_obj = existing_rating.scalar_one_or_none()

        if not rating_obj:
            rating_obj = Rating(
                user_id=user_id,
                content_id=content_id
            )
            session.add(rating_obj)

        return rating_obj

    @staticmethod
    async def save_feedback(user_id: int, content_id: int, is_helpful: bool, session):
        """Сохраняет обратную связь пользователя."""
        rating_obj = await RatingService.get_or_create_rating(user_id, content_id, session)
        rating_obj.is_helpful = is_helpful
        session.add(rating_obj)
        await session.commit()
        return rating_obj

    @staticmethod
    async def save_rating(user_id: int, content_id: int, score: int, session):
        """Сохраняет оценку пользователя."""
        rating_obj = await RatingService.get_or_create_rating(user_id, content_id, session)
        rating_obj.score = score
        session.add(rating_obj)
        await session.commit()
        return rating_obj
