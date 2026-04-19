# English Level Test Bot

Telegram-бот для определения уровня английского языка (A1–C2) по методике CEFR.

## Возможности

- 30 вопросов по 3 категориям: grammar, vocabulary, reading
- 6 уровней CEFR: A1, A2, B1, B2, C1, C2
- Таймер 20 минут на весь тест
- Детальный разбор ошибок после теста
- История результатов в SQLite
- Rate limiting (20 запросов/мин на пользователя)
- Логирование с ротацией
- Интеграция с Sentry

## Локальный запуск

```bash
# 1. Склонировать и перейти в директорию
cd "TG Bot"

# 2. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Создать .env из шаблона
cp .env.example .env
# Отредактировать .env и вставить TELEGRAM_BOT_TOKEN

# 5. Запустить
python main.py
```

## Деплой через Docker (рекомендуется)

```bash
# 1. Создать .env
cp .env.example .env
nano .env    # вставить токен

# 2. Запустить
docker compose up -d

# 3. Проверить логи
docker compose logs -f

# Управление
docker compose restart   # перезапуск
docker compose down      # остановка
docker compose pull && docker compose up -d --build    # обновление
```

Данные (БД и логи) сохраняются в `./data/` и `./logs/` на хосте.

## Деплой через systemd (Ubuntu/Debian)

```bash
# 1. Залить код на сервер
scp -r . user@server:/tmp/english-bot

# 2. На сервере
cd /tmp/english-bot
sudo bash deploy/install.sh

# 3. Создать .env
sudo cp /opt/english-bot/.env.example /opt/english-bot/.env
sudo nano /opt/english-bot/.env

# 4. Запустить
sudo systemctl start english-bot

# Проверка
sudo systemctl status english-bot
sudo journalctl -u english-bot -f
```

## Переменные окружения

| Переменная | Обязательна | Описание |
|------------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | ✅ | Токен от @BotFather |
| `SENTRY_DSN` | — | DSN для мониторинга ошибок |
| `ENVIRONMENT` | — | `development` или `production` |
| `LOG_LEVEL` | — | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `DATABASE_PATH` | — | Путь к SQLite БД |
| `TEST_TIME_LIMIT` | — | Таймаут теста в секундах |

## Структура проекта

```
.
├── main.py                    # Entry point
├── questions.py               # База из 30 вопросов
├── bot/
│   ├── handlers.py            # Хендлеры команд
│   ├── keyboards.py           # Клавиатуры
│   ├── database.py            # SQLite
│   ├── rate_limiter.py        # Ограничение частоты
│   ├── error_handler.py       # Глобальный обработчик ошибок
│   └── logger.py              # Настройка логов
├── deploy/
│   ├── english-bot.service    # systemd unit
│   └── install.sh             # Скрипт установки
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── .gitignore
```

## Команды бота

- `/start` — приветствие
- `/test` — начать тест
- `/result` — последние 5 результатов + лучший
- `/help` — справка

## Мониторинг

Логи:
- `logs/bot.log` — все события (ротация 10 МБ × 5)
- `logs/errors.log` — только ошибки
- `journalctl -u english-bot` — через systemd

Sentry — при указанном `SENTRY_DSN` все ошибки автоматически отправляются туда.

## Безопасность

⚠️ **Никогда не коммить `.env` файл**. Токен бота даёт полный контроль над ботом.

Если токен утёк — сбрось его через @BotFather: `/revoke`.
