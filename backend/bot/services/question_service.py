from logging import getLogger

from aiogram.types import Message, User
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from data.db import get_session
from data.models import Question
from data.queries import get_or_create_user
from bot.keyboards.main_menu import get_admin_answer_keyboard
from bot.urls import URLBuilder

logger = getLogger(__name__)


class QuestionService:
    """Сервис для работы с вопросами."""

    @staticmethod
    async def process_user_question(message: Message, state: FSMContext, admins: list, admin_url: str):
        """Обрабатывает вопрос от пользователя."""

        tg_user: User = getattr(message, "from_user")
        async with get_session() as session:
            user = await get_or_create_user(tg_user=tg_user, session=session)
            new_question = Question(text=message.text, user_id=user.telegram_id)
            session.add(new_question)
            await session.commit()
            await session.refresh(new_question)

            question_url = URLBuilder.get_admin_question_url(new_question.id)
            logger.info(
                f"New question #{new_question.id} "
                f"from user {message.from_user.id}"
                f"<i>Ссылка: {question_url}</i>"
            )

            await message.answer(
                "✅ Спасибо! Ваш вопрос отправлен администратору. "
                "Мы сообщим вам, как только поступит ответ."
            )
            await state.clear()

            # Формируем сообщение для админов
            admin_message = (
                f"❓ <b>Новый вопрос #{new_question.id}</b>\n\n"
                f"<b>От пользователя:</b> @{user.username}\n\n"
                f"<b>Текст вопроса:</b>\n{message.text}\n\n"
                f'<a href="{question_url}">Перейти к вопросу</a>'
            )

            for admin_id in admins:
                try:
                    await message.bot.send_message(
                        chat_id=admin_id,
                        text=admin_message,
                        reply_markup=await get_admin_answer_keyboard(
                            new_question.id
                        ),
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.exception(
                        "Failed to send question "
                        f"to admin {admin_id}: {e}"
                    )

    @staticmethod
    async def process_admin_answer(message: Message, state: FSMContext):
        """Обрабатывает ответ от администратора."""
        data = await state.get_data()
        question_id = data.get("question_id")

        if not question_id:
            await message.answer(
                "Произошла ошибка, не удалось определить вопрос. "
                "Попробуйте снова."
            )
            await state.clear()
            return

        user_id_to_notify = None

        async with get_session() as session:
            stmt = select(Question).where(Question.id == question_id)
            result = await session.execute(stmt)
            question = result.scalar_one_or_none()
            
            if not question:
                await message.answer(
                    f"Вопрос # {question_id} не найден в базе данных."
                )
                await state.clear()
                return

            question.answer_text = message.text
            user_id_to_notify = question.user_id
            await session.commit()

        user_message = (
            "<b>✅ Ответ на ваш вопрос от "
            f"{question.created_at.strftime('%d.%m.%Y %H:%M')}</b>\n\n"
            f"{message.text}"
        )

        try:
            await message.bot.send_message(
                chat_id=user_id_to_notify,
                text=user_message,
                parse_mode="HTML"
            )
            await message.answer(
                f"✅ Ответ на вопрос #{question_id} "
                "успешно отправлен пользователю."
            )
        except Exception as e:
            await message.answer(
                "⚠️ Не удалось отправить ответ пользователю "
                f"{user_id_to_notify}. Ошибка: {e}")

        await state.clear()
