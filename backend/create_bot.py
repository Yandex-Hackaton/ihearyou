import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from decouple import Config, RepositoryEnv


config = Config(RepositoryEnv('.env.dev'))


admins = [int(admin_id) for admin_id in config('ADMINS').split(',')]

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

bot = Bot(token=config('BOT_TOKEN'))

dp = Dispatcher(storage=MemoryStorage())