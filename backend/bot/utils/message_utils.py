from aiogram.types import CallbackQuery


async def safe_edit_message(
    callback: CallbackQuery,
    text: str,
    reply_markup=None,
    parse_mode="HTML",
    disable_web_page_preview=True
):
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


async def safe_delete_and_send(
    callback: CallbackQuery,
    text: str,
    reply_markup=None,
    parse_mode="HTML",
    disable_web_page_preview=True
):
    # Удаляем старое сообщение
    await callback.message.delete()

    # Отправляем новое сообщение
    await callback.message.answer(
        text,
        reply_markup=reply_markup,
        parse_mode=parse_mode,
        disable_web_page_preview=disable_web_page_preview
    )
