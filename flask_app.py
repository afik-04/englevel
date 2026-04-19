"""WSGI-приложение для деплоя на PythonAnywhere (webhook режим).

На PythonAnywhere укажи этот файл в разделе Web → WSGI configuration.
Переменная `application` — это то, что PythonAnywhere будет запускать.
"""
import asyncio
import logging
import os
from flask import Flask, request, Response
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv

load_dotenv()

from bot.logger import setup_logging
setup_logging()

from bot.handlers import start, start_test, handle_answer, help_command, result_command
from bot.error_handler import error_handler
from bot.database import init_db

logger = logging.getLogger(__name__)

# Sentry
sentry_dsn = os.getenv("SENTRY_DSN", "").strip()
if sentry_dsn:
    try:
        import sentry_sdk
        sentry_sdk.init(dsn=sentry_dsn, traces_sample_rate=0.1)
    except ImportError:
        pass

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "secret")

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN не задан")

init_db()

# Создаём PTB Application без встроенного updater (webhook режим)
telegram_app = ApplicationBuilder().token(TOKEN).updater(None).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("test", start_test))
telegram_app.add_handler(CommandHandler("help", help_command))
telegram_app.add_handler(CommandHandler("result", result_command))
telegram_app.add_handler(CallbackQueryHandler(handle_answer))
telegram_app.add_error_handler(error_handler)

# Инициализируем application один раз
_loop = asyncio.new_event_loop()
_loop.run_until_complete(telegram_app.initialize())
_loop.run_until_complete(telegram_app.start())

application = Flask(__name__)


@application.route("/", methods=["GET"])
def index():
    return "Bot is running"


@application.route(f"/webhook/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    """Принимает update от Telegram и передаёт его в PTB."""
    try:
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, telegram_app.bot)
        _loop.run_until_complete(telegram_app.process_update(update))
        return Response("OK", status=200)
    except Exception as e:
        logger.exception(f"Ошибка обработки webhook: {e}")
        return Response("Error", status=500)


if __name__ == "__main__":
    # Для локального тестирования
    application.run(host="0.0.0.0", port=5000)
