from aiogram.types import CallbackQuery


async def safe_edit_message(
    callback: CallbackQuery,
    text: str,
    reply_markup=None,
    parse_mode="HTML",
    disable_web_page_preview=True
):
    """
    Безопасно редактирует сообщение, учитывая наличие медиа.

    Args:
        callback: CallbackQuery объект
        text: Текст для отображения
        reply_markup: Клавиатура (опционально)
        parse_mode: Режим парсинга (по умолчанию HTML)
        disable_web_page_preview: Отключить превью ссылок
    """
    if callback.message.photo:
        # Если есть фото, редактируем caption
        await callback.message.edit_caption(
            caption=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
    else:
        # Если нет медиа, редактируем текст
        await callback.message.edit_text(
            text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview
        )
