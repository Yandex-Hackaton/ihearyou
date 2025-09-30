import json
from contextlib import asynccontextmanager
from pathlib import Path

from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from decouple import config

from .models import User

# Конфигурация базы данных
postgres_url = config("POSTGRES_CONN_STRING")

# Создание движка и сессии
engine = create_async_engine(postgres_url, echo=False)
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_session():
    """Контекстный менеджер для работы с сессией базы данных."""
    session = async_session()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def create_db_and_tables():
    """Создание таблиц в базе данных."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def load_fixtures(file_name: str):
    """Загрузка фикстур в базу данных."""
    await create_db_and_tables()

    BASE_DIR = Path(__file__).resolve().parent
    fixture_path = BASE_DIR / "fixtures" / file_name

    # Загружаем данные из файла
    try:
        with open(fixture_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return

    # Работаем с базой данных в отдельной сессии
    async with get_session() as session:
        try:
            for item in data:
                if file_name == 'initial_data.json':
                    # Проверяем, существует ли пользователь
                    existing_user = await session.execute(
                        select(User).where(User.telegram_id == item['telegram_id'])
                    )
                    if not existing_user.scalar_one_or_none():
                        session.add(User(**item))

        except Exception as e:
            raise e
