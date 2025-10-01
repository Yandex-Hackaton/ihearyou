from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin
from starlette.middleware.sessions import SessionMiddleware

from .config import AdminConfig
from .auth import AdminAuthBackend
from admin.view import (
    CategoryView,
    ContentView,
    QuestionView,
    UserView,
    InteractionEventView,
)
from data.db import engine, create_db_and_tables, load_fixtures
from utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting admin panel...")

    await create_db_and_tables()
    await load_fixtures("initial_data.json")

    logger.info("Admin panel started successfully")
    yield

    logger.info("Admin panel stopped")


app = FastAPI(
    title=AdminConfig.TITLE,
    version=AdminConfig.VERSION,
    lifespan=lifespan,
)

# Добавляем middleware для сессий
app.add_middleware(
    SessionMiddleware,
    secret_key=AdminConfig.SESSION_SECRET_KEY,
    session_cookie=AdminConfig.SESSION_COOKIE_NAME,
)

# Регистрируем статические файлы для админки
app.mount("/static", StaticFiles(directory="admin/statics"), name="static")


# Настраиваем SQLAdmin с кастомными шаблонами и аутентификацией
admin = Admin(
    app,
    engine,
    title=AdminConfig.ADMIN_TITLE,
    templates_dir="admin/templates",
    authentication_backend=AdminAuthBackend(secret_key=AdminConfig.SESSION_SECRET_KEY),
)

# Регистрация views
admin.add_view(UserView)
admin.add_view(CategoryView)
admin.add_view(ContentView)
admin.add_view(QuestionView)
admin.add_view(InteractionEventView)
