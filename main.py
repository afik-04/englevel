import logging
import os
import sys
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv

load_dotenv()

from bot.logger import setup_logging
setup_logging()

from bot.handlers import start, start_test, handle_answer, help_command, result_command
from bot.error_handler import error_handler
from bot.database import init_db

logger = logging.getLogger(__name__)

# Инициализация Sentry (если DSN указан)
sentry_dsn = os.getenv("SENTRY_DSN", "").strip()
if sentry_dsn:
    try:
        import sentry_sdk
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=os.getenv("ENVIRONMENT", "development"),
            traces_sample_rate=0.1,
        )
        logger.info("Sentry инициализирован")
    except ImportError:
        logger.warning("sentry_sdk не установлен — мониторинг ошибок отключён")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN не задан в .env")
    sys.exit(1)

init_db()
logger.info("База данных инициализирована")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("test", start_test))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("result", result_command))
app.add_handler(CallbackQueryHandler(handle_answer))
app.add_error_handler(error_handler)

logger.info("Бот запущен")
try:
    app.run_polling(allowed_updates=["message", "callback_query"])
except KeyboardInterrupt:
    logger.info("Бот остановлен вручную")
except Exception as e:
    logger.exception(f"Критическая ошибка: {e}")
    sys.exit(1)
