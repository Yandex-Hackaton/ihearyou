import logging

from decouple import config

logger = logging.getLogger(__name__)

ADMINS = list(map(int, config('ADMINS').split()))

ADMIN_QUESTION_URL = "https://www.stepaxvii.ru//admin/question/details/"
