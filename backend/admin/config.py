from dataclasses import dataclass


@dataclass
class AdminConfig:
    TITLE: str = "IHearYou Admin Panel"
    VERSION: str = "1.0.0"
    ADMIN_TITLE: str = "IHearYou Admin"

    # Секретный ключ для сессий
    SESSION_SECRET_KEY: str = "your-secret-key-here"
    SESSION_COOKIE_NAME: str = "admin_session"

    # Настройки UI
    PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
