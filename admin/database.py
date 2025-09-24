from sqlmodel import SQLModel, create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ihearyou:ihearyou_password@localhost:5432/ihearyou")

engine = create_engine(
    DATABASE_URL, 
    echo=True,
    pool_pre_ping=True,
    pool_recycle=300,
)

def create_tables():
    """Создает все таблицы в базе данных"""
    SQLModel.metadata.create_all(engine)

create_tables()