from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine
from sqladmin import Admin, ModelView
from admin.models import User
from dotenv import load_dotenv
from decouple import config

load_dotenv()

DATABASE_URL: str = config('DB_CONNECTION_STRING')

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