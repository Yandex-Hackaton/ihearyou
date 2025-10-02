import os

from utils.logger import logger


admins_raw_str = os.getenv("ADMINS", "")
ADMINS = []
if admins_raw_str:
    for admin_id_str in admins_raw_str.split(','):
        try:
            ADMINS.append(int(admin_id_str.strip()))
        except ValueError:
            logger.warning(
                f"Некорректный ID администратора в .env: '{admin_id_str}'."
                )

ADMIN_QUESTION_URL = "https://www.ihearyou.ru//admin/question/details/"
