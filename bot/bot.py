import asyncio
from logging import getLogger

from aiogram import Bot, Dispatcher
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from core.config import config
from core.db import init_db
from stats.middleware import InteractionEventMiddleware

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

logger = getLogger(__name__)


@dp.message()
async def echo_message(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Кнопка 1", callback_data="btn_1"),
                InlineKeyboardButton(text="Кнопка 2", callback_data="btn_2"),
            ],
            [
                InlineKeyboardButton(text="Кнопка 3", callback_data="btn_3"),
            ],
        ]
    )

    await message.answer(
        f"Вы написали: {message.text}",
        reply_markup=keyboard,
    )


@dp.callback_query()
async def echo_callback(callback: CallbackQuery):
    logger.info(f"Пользователь {callback.from_user.id} нажал кнопку: {callback.data}")
    await callback.answer()


def setup_middlewares(dp: Dispatcher):
    dp.message.middleware(InteractionEventMiddleware())
    dp.callback_query.middleware(InteractionEventMiddleware())


async def main():
    setup_middlewares(dp)
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
