from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from core.config import config
from stats.models import InteractionEvent  # noqa: F401

engine = create_async_engine(
    config.database_url.get_secret_value(),
    pool_pre_ping=True,
    pool_recycle=300,
)
async_session = async_sessionmaker(engine)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
