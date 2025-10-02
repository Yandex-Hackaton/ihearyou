import logging

from fastapi import Request
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select

from data.db import get_session
from data.models import User
from enums.msg import AuthAdmin

logger = logging.getLogger(__name__)


class AdminAuthBackend(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get('username')
        password = form.get('password')

        if not username or not password:
            logger.warning('Admin login attempt with empty credentials')
            return False

        # Получаем сессию базы данных
        async with get_session() as session:
            # Ищем пользователя по username и проверяем, что он админ
            stmt = select(User).where(
                User.username == username, User.is_admin,
            )
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                logger.warning(
                    f'{AuthAdmin.LOGIN_FAILED.value}: '
                    f'user not found or not admin - {username}'
                )
                return False

            # Простая проверка пароля (без хеширования)
            if password != user.password:
                logger.warning(
                    f'{AuthAdmin.LOGIN_FAILED.value}: '
                    f'wrong password - {username}'
                )
                return False

            # Сохраняем информацию о пользователе в сессии
            request.session.update({'user_id': user.telegram_id})
            logger.info(
                f'{AuthAdmin.LOGIN_SUCCESSFUL.value}: '
                f'{username} (ID: {user.telegram_id})'
            )
            return True

    async def logout(self, request: Request) -> bool:
        user_id = request.session.get('user_id')
        logger.info(
            f'{AuthAdmin.LOGOUT.value}: user_id={user_id}'
        )
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        user_id = request.session.get('user_id')
        if not user_id:
            return False

        # Проверяем, что пользователь все еще существует и является админом
        async with get_session() as session:
            stmt = select(User).where(
                User.telegram_id == user_id, User.is_admin
            )
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if user is None:
                logger.warning(
                    f'{AuthAdmin.AUTH_FAILED.value}: '
                    f'user not found or not admin - {user_id}'
                )
            return user is not None
