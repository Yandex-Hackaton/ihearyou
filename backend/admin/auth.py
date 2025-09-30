from typing import Optional
from fastapi import Request
from sqlalchemy import select
from sqladmin.authentication import AuthenticationBackend

from data.models import User
from data.db import async_session


class AdminAuthBackend(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if not username or not password:
            return False

        # Получаем сессию базы данных
        async with async_session() as session:
            # Ищем пользователя по username и проверяем, что он админ
            stmt = select(User).where(
                User.username == username,
                User.is_admin == True
            )
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                return False

            # Простая проверка пароля (без хеширования)
            if password != user.password:
                return False

            # Сохраняем информацию о пользователе в сессии
            request.session.update({"user_id": user.telegram_id})
            return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        user_id = request.session.get("user_id")
        if not user_id:
            return False

        # Проверяем, что пользователь все еще существует и является админом
        async with async_session() as session:
            stmt = select(User).where(
                User.telegram_id == user_id,
                User.is_admin == True
            )
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            return user is not None
