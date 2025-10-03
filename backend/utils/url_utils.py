import re
import unicodedata


def clean_url(url: str) -> str:
    """Очищает URL от невидимых символов и лишних пробелов."""
    if not url:
        return url

    cleaned = ''.join(
        char for char in url if unicodedata.category(char) != 'Cf'
    )
    cleaned = cleaned.strip()

    return cleaned


def is_valid_image_url(url: str) -> bool:
    """Проверяет, является ли URL валидным для изображения."""
    if not url or not url.strip():
        return False

    # Очищаем URL от невидимых символов
    url = clean_url(url)

    # Проверяем, что это Telegram file URL
    telegram_pattern = r'^https://api\.telegram\.org/file/bot[\w-]+/.*'
    if re.match(telegram_pattern, url):
        return True

    # Проверяем другие популярные форматы изображений
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    url_lower = url.lower()

    return any(url_lower.endswith(ext) for ext in image_extensions)
