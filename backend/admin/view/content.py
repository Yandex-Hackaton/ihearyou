from starlette.requests import Request
from sqlalchemy.orm import selectinload

from data.models import Content
from admin.base import CustomModelView
from enums.fields import ViewLimits, Formats


class ContentView(CustomModelView, model=Content):
    name = "Контент"
    name_plural = "Контент"
    icon = "fa-solid fa-file-lines"

    # Названия полей
    column_labels = {
        Content.id: "ID",
        Content.title: "Название",
        Content.description: "Краткое описание",
        Content.url_link: "Ссылка",
        Content.is_active: "Активно",
        Content.views_count: "Просмотры",
        Content.category: "Категория",
        Content.created_at: "Дата и время создания",
        "rating_helpful_percent": "Процент полезности",
        "rating_average": "Средний рейтинг",
    }

    # Поля на странице списка
    column_list = [
        Content.id,
        Content.title,
        Content.category,
        Content.views_count,
        Content.is_active,
        Content.created_at,
    ]

    # Поля на странице детальной информации
    column_details_list = [
        Content.id,
        Content.title,
        Content.description,
        Content.url_link,
        Content.is_active,
        Content.views_count,
        "rating_helpful_percent",
        "rating_average",
        Content.category,
        Content.created_at,
    ]

    # Поля доступные для изменений
    form_columns = [
        Content.title,
        Content.description,
        Content.url_link,
        Content.is_active,
        Content.category,
    ]

    def list_query(self, request: Request):
        return (
            super()
            .list_query(request)
            .options(selectinload(Content.category))
            .options(selectinload(Content.ratings))
        )

    def details_query(self, request: Request):
        from data.models import Rating

        return (
            super()
            .details_query(request)
            .options(selectinload(Content.category))
            .options(selectinload(Content.ratings).selectinload(Rating.user))
        )

    @staticmethod
    def format_category(model: Content, attribute) -> str:
        return model.category.title if model.category else "Без категории"

    @staticmethod
    def format_datetime(model: Content, attribute) -> str:
        return model.created_at.strftime(Formats.DATETIME.value)

    @staticmethod
    def format_views(model: Content, attribute) -> str:
        return f"{model.views_count} просм."

    @staticmethod
    def format_rating_helpful(model, attribute):
        """Форматирование количества положительных оценок."""
        stats = ContentView.get_rating_stats(model.ratings)
        return f"{stats['helpful']} из {stats['total']}"

    @staticmethod
    def format_rating_not_helpful(model, attribute):
        """Форматирование количества отрицательных оценок."""
        stats = ContentView.get_rating_stats(model.ratings)
        return f"{stats['not_helpful']} из {stats['total']}"

    @staticmethod
    def format_rating_helpful_percent(model: Content, attribute):
        """Форматирование процента полезности."""
        stats = ContentView.get_rating_stats(model.ratings)
        if stats["total"] > 0:
            return f"{stats['helpful_percent']:.1f}%"
        return "Нет оценок"

    @staticmethod
    def format_rating_average(model, attribute):
        """Форматирование среднего рейтинга."""
        stats = ContentView.get_rating_stats(model.ratings)
        if stats["avg_rating"] is not None:
            return f"{stats['avg_rating']:.2f} / 5.00"
        return "Нет оценок"

    @staticmethod
    def get_rating_stats(ratings):
        """Получить статистику по рейтингам."""
        if not ratings:
            return {
                "total": 0,
                "helpful": 0,
                "not_helpful": 0,
                "avg_rating": None,
                "helpful_percent": 0,
            }

        total = len(ratings)
        helpful = sum(1 for r in ratings if r.is_helpful is True)
        not_helpful = sum(1 for r in ratings if r.is_helpful is False)
        ratings_with_value = [
            r.score for r in ratings if r.score is not None
        ]
        avg_rating = (
            sum(ratings_with_value) / len(ratings_with_value)
            if ratings_with_value
            else None
        )
        helpful_percent = (helpful / total * 100) if total > 0 else 0

        return {
            "total": total,
            "helpful": helpful,
            "not_helpful": not_helpful,
            "avg_rating": avg_rating,
            "helpful_percent": helpful_percent,
        }

    @staticmethod
    def truncate_description(model: Content, attribute) -> str:
        text = model.description or ""
        return (
            (text[:ViewLimits.TEXT_FIELD.value] + "…")
            if len(text) > ViewLimits.TEXT_FIELD.value else text
        )

    column_formatters = {
        Content.description: truncate_description,
        Content.category: format_category,
        Content.created_at: format_datetime,
        Content.views_count: format_views,
    }

    column_formatters_detail = {
        Content.category: format_category,
        Content.created_at: format_datetime,
        Content.views_count: format_views,
        "rating_helpful_percent": format_rating_helpful_percent,
        "rating_average": format_rating_average,
    }

    async def get_details(self, request, pk):
        """Переопределяем для добавления статистики рейтингов."""
        obj = await super().get_details(request, pk)
        if obj and hasattr(obj, "ratings"):
            stats = self.get_rating_stats(obj.ratings)
            obj._rating_stats = stats
        return obj
