import json
from pathlib import Path
from typing import AsyncGenerator

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from decouple import Config, RepositoryEnv

from .models import User


config = Config(RepositoryEnv('.env.dev'))

postgres_url = config("POSTGRES_CONN_STRING")

engine = create_async_engine(postgres_url, echo=True)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    print("Таблицы созданы успешно!")


async def load_fixtures(file_name: str):
    await create_db_and_tables()

    BASE_DIR = Path(__file__).resolve().parent
    fixture_path = BASE_DIR / "fixtures" / file_name

    async for session in get_session():
        try:
            with open(fixture_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f'❌ Файл фикстуры не найден: {fixture_path}')

    for item in data:
        session.add(User(**item))
    try:
        await session.commit()
    except IntegrityError:
        print('❌ Данные уже существуют')
        return

    print(f"✅ Фикстура '{fixture_path}' успешно загружена в базу данных.")
