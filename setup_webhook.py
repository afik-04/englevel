"""Одноразовый скрипт для регистрации webhook URL в Telegram.

Запусти на PythonAnywhere после настройки Web App:
    python setup_webhook.py

Или с аргументом для удаления webhook (чтобы снова работал polling):
    python setup_webhook.py delete
"""
import os
import sys
import asyncio
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PYTHONANYWHERE_USERNAME = os.getenv("PYTHONANYWHERE_USERNAME")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "secret")


async def set_webhook():
    if not PYTHONANYWHERE_USERNAME:
        print("❌ Укажи PYTHONANYWHERE_USERNAME в .env")
        sys.exit(1)

    url = f"https://{PYTHONANYWHERE_USERNAME}.pythonanywhere.com/webhook/{WEBHOOK_SECRET}"
    bot = Bot(token=TOKEN)
    await bot.set_webhook(
        url=url,
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True
    )
    info = await bot.get_webhook_info()
    print(f"✅ Webhook установлен: {info.url}")


async def delete_webhook():
    bot = Bot(token=TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Webhook удалён — можно снова использовать polling")


async def info():
    bot = Bot(token=TOKEN)
    webhook_info = await bot.get_webhook_info()
    print(f"URL: {webhook_info.url or '(не установлен)'}")
    print(f"Pending updates: {webhook_info.pending_update_count}")
    if webhook_info.last_error_message:
        print(f"❌ Последняя ошибка: {webhook_info.last_error_message}")


if __name__ == "__main__":
    if not TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN не задан в .env")
        sys.exit(1)

    cmd = sys.argv[1] if len(sys.argv) > 1 else "set"

    if cmd == "delete":
        asyncio.run(delete_webhook())
    elif cmd == "info":
        asyncio.run(info())
    else:
        asyncio.run(set_webhook())
