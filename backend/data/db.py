import asyncio
from sqlmodel import SQLModel
from decouple import config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

postgres_url = config("POSTGRES_CONN_STRING")

engine = create_async_engine(postgres_url, echo=True)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    print("Таблицы созданы успешно!")


async def init_db_with_test_data():
    """Инициализация базы данных с созданием таблиц и тестовых данных"""
    from .seed_data import create_test_data
    
    await create_db_and_tables()
    
    await create_test_data()


async def get_session():
    async with async_session() as session:
        yield session


if __name__ == "__main__":
    asyncio.run(init_db_with_test_data())
