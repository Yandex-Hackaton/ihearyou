from dataclasses import dataclass
from decouple import config


@dataclass
class AdminConfig:
    TITLE: str = 'IHearYou Admin Panel'
    VERSION: str = '1.0.0'
    ADMIN_TITLE: str = 'IHearYou Admin'

    # Секретный ключ для сессий
    SESSION_SECRET_KEY: str = config(
        'SESSION_SECRET_KEY',
        default='your-secret-key-here',
    )
    SESSION_COOKIE_NAME: str = config(
        'SESSION_COOKIE_NAME',
        default='admin_session',
    )

    # Настройки UI
    PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
