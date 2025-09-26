from sqlmodel import SQLModel, create_engine
from decouple import config

from models import User, Role, Button, Category


sqlite_file_name = config('DB_NAME')
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(
    sqlite_url,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={'check_same_thread': False},
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
