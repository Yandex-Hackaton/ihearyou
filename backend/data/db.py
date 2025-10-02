import json
from collections.abc import AsyncGenerator

from decouple import config
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel, select
from contextlib import asynccontextmanager

from .model_mapping import MODEL_MAP
from .constants import FIXTURE_PATH


# Конфигурация базы данных
postgres_url = config('POSTGRES_CONN_STRING')

# Создание движка и сессии
engine = create_async_engine(postgres_url, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def create_db_and_tables():
    '''Создание таблиц в базе данных.'''
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def load_fixtures(file_name):
    '''Загрузка фикстур в базу данных.'''
    await create_db_and_tables()
    with open(FIXTURE_PATH / file_name, 'r', encoding='utf-8') as f:
        fixtures = json.load(f)

    # Загружаем данные из файла
    async with get_session() as session:
        for fixture in fixtures:
            model = MODEL_MAP[fixture['table']]

            # Проверяем, пуста ли таблица
            result = await session.execute(select(model))
            if result.first() is not None:
                continue

            # Добавляем данные, если таблица пустая
            for row in fixture['rows']:
                session.add(model(**row))

        await session.commit()
