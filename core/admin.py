from fastapi import FastAPI
from sqladmin import Admin

from core.db import engine
from stats.admin import InteractionEventAdmin

app = FastAPI(title="Telegram Bot Admin Panel", version="1.0.0")

admin = Admin(app, engine, title="Управление Telegram Ботом")
admin.add_view(InteractionEventAdmin)
