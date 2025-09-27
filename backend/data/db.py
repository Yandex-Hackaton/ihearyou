import asyncio
from sqlmodel import SQLModel
from decouple import config
from sqlalchemy.ext.asyncio import create_async_engine
from models import User, Role, Button, Category


postgres_url = config('POSTGRES_CONN_STRING')


# Функция для первичного создания всех таблиц в Postgres контейнере Docker
async def main():
    engine = create_async_engine(postgres_url)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(main())
