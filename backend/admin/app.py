from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin
from starlette.middleware.sessions import SessionMiddleware

from .config import AdminConfig
from .auth import AdminAuthBackend
from admin.view import CategoryView, ContentView, QuestionView, UserView
from data.db import engine, create_db_and_tables, load_fixtures


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    await load_fixtures('initial_data.json')
    await load_fixtures('test_questions.json') 
    yield

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

# Регистрируем статические файлы для изображений (для ImageType)
app.mount("/media", StaticFiles(directory="media"), name="media")

# Настраиваем SQLAdmin с кастомными шаблонами и аутентификацией
admin = Admin(
    app, 
    engine, 
    title=AdminConfig.ADMIN_TITLE,
    templates_dir="admin/templates",
    authentication_backend=AdminAuthBackend(secret_key=AdminConfig.SESSION_SECRET_KEY)
)

# Регистрация views
admin.add_view(UserView)
admin.add_view(CategoryView)
admin.add_view(ContentView)
admin.add_view(QuestionView)