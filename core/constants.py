import os
from typing import cast

from dotenv import load_dotenv

load_dotenv()

TOKEN: str = cast(str, os.getenv("BOT_TOKEN"))
DEBUG = os.getenv("DEBUG", "False") in ("True", "true", "1", "yes")
DATABASE_URL: str = cast(str, os.getenv("DATABASE_URL"))
assert DATABASE_URL
assert TOKEN
