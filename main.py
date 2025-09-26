import asyncio

from bot.bot import main
from core.admin import app
from core.logging import setup_logging

app = app

if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())
