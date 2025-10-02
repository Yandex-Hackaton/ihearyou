class URLs:
    """Класс для хранения всех URL проекта."""

    # Основные URL сайта
    SITE_URL = "https://www.ihearyou.ru"

    # Админ панель
    ADMIN_QUESTION_URL = "https://www.stepaxvii.ru/admin/question/details/"
    ADMIN_STATS_URL = "https://stepaxvii.ru/admin/interaction-event/list"
    ADMIN_QUESTION_LIST_URL = "https://stepaxvii.ru/admin/question/list"
    ADMIN_STATS_LIST_URL = "https://stepaxvii.ru/admin/interaction-event/list"

    # Telegram API
    TELEGRAM_API_BASE = "https://api.telegram.org/file/bot"

    # Социальные сети и ресурсы
    VK_URL = "https://vk.com/ihear_you"
    DZEN_URL = "https://dzen.ru/ihearyou"
    CLUB_URL = "https://ятебяслышу.рф/ihearyouclub"

    # Подкасты
    APPLE_PODCASTS_URL = (
        "https://podcasts.apple.com/ru/podcast/"
        "не-понаслышке/id1530818421"
    )
    YANDEX_MUSIC_URL = "https://music.yandex.ru/album/12068742"

    # Полезные статьи
    HEARING_LOSS_ARTICLE = (
        "https://www.ihearyou.ru/materials/articles/"
        "kak-uznat-chto-snizhen-slukh"
    )
    FAMILY_IMPACT_ARTICLE = (
        "https://www.ihearyou.ru/materials/articles/"
        "vliyanie-poteri-slukha-na-semyu"
    )


class URLBuilder:
    """Утилиты для построения URL."""

    @staticmethod
    def get_telegram_file_url(bot_token: str, file_path: str) -> str:
        """Строит URL для файла Telegram."""
        return f"{URLs.TELEGRAM_API_BASE}{bot_token}/{file_path}"

    @staticmethod
    def get_admin_question_url(question_id: int) -> str:
        """Строит URL для просмотра вопроса в админ панели."""
        return f"{URLs.ADMIN_QUESTION_URL}{question_id}"

    @staticmethod
    def get_useful_materials_text() -> str:
        """Возвращает HTML текст с полезными материалами."""
        return (
            "<b>📚 Полезные материалы</b>\n\n"
            f'<a href="{URLs.SITE_URL}">Наш сайт</a>\n\n'
            f'<a href="{URLs.CLUB_URL}">Клуб "Я тебя слышу"</a>\n\n'
            f'<a href="{URLs.VK_URL}">VK</a>\n'
            f'<a href="{URLs.DZEN_URL}">Дзен</a>\n\n'
            '<b>Подкаст "Не понаслышке":</b>\n'
            f'<a href="{URLs.APPLE_PODCASTS_URL}">Подкасты Apple</a>\n'
            f'<a href="{URLs.YANDEX_MUSIC_URL}">Яндекс Музыка</a>'
        )

    @staticmethod
    def get_reminder_texts() -> dict:
        """Возвращает тексты напоминаний с URL."""
        return {
            "bot": (
                "Привет! Напоминаем, что бот «Я Тебя Слышу» всегда рядом.\n"
                "Здесь ты можешь найти статьи, советы и поддержку. "
                "Загляни, когда будет время 🌿\n\n"
                f"Как узнать, что снижен слух: {URLs.HEARING_LOSS_ARTICLE}\n"
                f"Влияние потери слуха на семью: {URLs.FAMILY_IMPACT_ARTICLE}"
            ),
            "auri": (
                "👋 Привет, это снова я — Аури!\n"
                "Ты давно не заглядывал в бот, и я немного скучал 💙\n"
                "У меня тут есть новые материалы и советы, которые могут быть "
                "полезны именно тебе. Загляни, когда будет настроение — "
                "я всегда рядом 🌟"
            )
        }
