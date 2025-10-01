from sqladmin import ModelView
from utils.logger import logger


class CustomModelView(ModelView):
    """Базовый класс для View с логированием"""

    def _get_model_id(self, model):
        """Получить правильный ID модели для логирования"""
        # Для User используем telegram_id
        if self.model.__name__ == 'User':
            return getattr(model, 'telegram_id', 'unknown')
        # Для остальных моделей используем обычный id
        return getattr(model, 'id', 'unknown')

    def _get_model_name(self):
        """Получить название модели для логирования"""
        return self.model.__name__.lower()

    async def on_model_change(self, data, model, is_created, request):
        """Логирование изменений моделей"""
        model_name = self._get_model_name()
        model_id = self._get_model_id(model)

        if is_created:
            logger.info(
                f"Admin created {model_name} (ID: {model_id})"
            )
        else:
            logger.info(
                f"Admin updated {model_name} (ID: {model_id})"
            )

    async def on_model_delete(self, model, request):
        """Логирование удаления моделей"""
        model_name = self._get_model_name()
        model_id = self._get_model_id(model)

        logger.warning(
            f"Admin deleted {model_name} (ID: {model_id})"
        )
