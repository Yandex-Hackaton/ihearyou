from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine
from sqladmin import Admin, ModelView
from admin.models import User
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://ihearyou:ihearyou_password@localhost:5432/ihearyou")

engine = create_engine(
    DATABASE_URL, 
    echo=True,
    pool_pre_ping=True,
    pool_recycle=300,
)

SQLModel.metadata.create_all(engine)

app = FastAPI(title="Telegram Bot Admin Panel", version="1.0.0")

admin = Admin(app, engine, title="Управление Telegram Ботом")

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username]
    column_searchable_list = [User.username]
    column_sortable_list = [User.id, User.username]

admin.add_view(UserAdmin)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)