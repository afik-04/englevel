import logging
import html
import traceback
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Глобальный обработчик ошибок — логирует и уведомляет пользователя."""
    logger.error("Exception while handling update:", exc_info=context.error)

    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)

    if isinstance(update, Update):
        update_info = html.escape(str(update.to_dict())[:500])
        logger.error(f"Update: {update_info}")

    logger.error(f"Traceback:\n{tb_string}")

    # Уведомляем пользователя
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ Произошла ошибка. Попробуй позже или нажми /start."
            )
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение об ошибке: {e}")
