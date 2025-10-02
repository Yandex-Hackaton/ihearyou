from typing import Any

from aiogram.types import Message, PhotoSize


class ValidationError(Exception):
    """Ошибка валидации."""
    pass


class ValidationResult:
    """Результат валидации."""

    def __init__(self, is_valid: bool, errors: list[str] = None,
                 data: Any = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.data = data

    def add_error(self, error: str):
        """Добавить ошибку."""
        self.errors.append(error)
        self.is_valid = False


class Validator:
    def validate(self, value: Any) -> ValidationResult:
        """Валидация значения."""
        raise NotImplementedError


class ImageValidator(Validator):
    def __init__(self, max_size: int = 20 * 1024 * 1024,  # 20MB
                 allowed_formats: list[str] = None):
        self.max_size = max_size
        self.allowed_formats = (
            allowed_formats or ['jpg', 'jpeg', 'png', 'gif', 'webp']
        )

    def validate(self, value: Any) -> ValidationResult:
        result = ValidationResult(True)

        if not value:
            result.add_error("Изображение обязательно")
            return result

        if not isinstance(value, PhotoSize):
            result.add_error("Значение должно быть изображением")
            return result

        if value.file_size and value.file_size > self.max_size:
            size_mb = self.max_size // (1024*1024)
            result.add_error(f"Размер файла превышает {size_mb}MB")

        return result


def validate_photo(message: Message, validator: Validator) -> ValidationResult:
    """Валидация фото."""
    if not message.photo:
        return ValidationResult(
            False, 
            ["Сообщение должно содержать изображение"]
        )

    return validator.validate(message.photo[-1])


class BotValidators:
    ADMIN_IMAGE = ImageValidator(
        max_size=10 * 1024 * 1024,
        allowed_formats=['jpg', 'jpeg', 'png']
    )


def format_description_with_breaks(description: str) -> str:
    if not description:
        return ""

    import re

    # Добавляем \n\n после эмодзи
    emoji_pattern = r'(💔|❓|💡|📖|🤗|👶|🎧|🔊)'
    formatted = re.sub(emoji_pattern, r'\1\n\n', description)

    return formatted
