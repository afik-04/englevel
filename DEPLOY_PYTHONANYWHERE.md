# Деплой на PythonAnywhere (бесплатно)

Пошаговая инструкция — от регистрации до работающего бота.

## Шаг 0. Подготовка

Нужен аккаунт на GitHub (для загрузки кода). Если нет — создай на [github.com](https://github.com).

### Залей код на GitHub

```bash
cd "Desktop/TG Bot"

git init
git add .
git commit -m "Initial commit"

# Создай репозиторий на github.com, затем:
git remote add origin https://github.com/ТВОЙ-USERNAME/tg-bot.git
git branch -M main
git push -u origin main
```

**Убедись что `.env` НЕ попал в репозиторий** (проверь на GitHub — его не должно быть).

---

## Шаг 1. Регистрация на PythonAnywhere

1. Заходи на [pythonanywhere.com](https://www.pythonanywhere.com/pricing/)
2. **Create a Beginner account** (бесплатно, без карты)
3. Придумай username — он станет частью URL (`username.pythonanywhere.com`)
4. Подтверди email

---

## Шаг 2. Загрузка кода

В PythonAnywhere открой **Consoles → Bash**:

```bash
# Склонируй код
git clone https://github.com/ТВОЙ-USERNAME/tg-bot.git
cd tg-bot

# Создай виртуальное окружение
python3.10 -m venv venv
source venv/bin/activate

# Установи зависимости
pip install -r requirements.txt
```

---

## Шаг 3. Настройка `.env`

В той же консоли:

```bash
cp .env.example .env
nano .env
```

Заполни:
```
TELEGRAM_BOT_TOKEN=твой_токен_от_botfather
PYTHONANYWHERE_USERNAME=твой_username_на_pythonanywhere
WEBHOOK_SECRET=любая_длинная_случайная_строка_abc123xyz
```

Сохрани: `Ctrl+O` → `Enter` → `Ctrl+X`

---

## Шаг 4. Создание Web App

1. Вкладка **Web → Add a new web app**
2. **Next** → **Manual configuration** (не Flask автоматически!)
3. Выбери **Python 3.10**
4. **Next**

### Настройка Virtualenv

На странице Web App найди секцию **Virtualenv** и введи:
```
/home/ТВОЙ-USERNAME/tg-bot/venv
```

### Настройка Source code

В секции **Code** укажи:
```
Source code:     /home/ТВОЙ-USERNAME/tg-bot
Working directory: /home/ТВОЙ-USERNAME/tg-bot
```

### Настройка WSGI

Кликни на файл WSGI configuration (обычно `/var/www/username_pythonanywhere_com_wsgi.py`).

Замени всё содержимое на:

```python
import sys
import os

# Путь к проекту
path = "/home/ТВОЙ-USERNAME/tg-bot"
if path not in sys.path:
    sys.path.insert(0, path)

# Загрузка .env
from dotenv import load_dotenv
load_dotenv(os.path.join(path, ".env"))

# Импорт Flask app
from flask_app import application
```

**Замени `ТВОЙ-USERNAME` на свой!**

Сохрани файл (Save).

---

## Шаг 5. Запуск Web App

1. Возвращайся на вкладку **Web**
2. Нажми зелёную кнопку **Reload**
3. Открой URL `https://ТВОЙ-USERNAME.pythonanywhere.com`
4. Должно показать: **Bot is running**

Если ошибка — проверь логи в разделе **Log files → Error log**.

---

## Шаг 6. Регистрация webhook в Telegram

В консоли **Bash** на PythonAnywhere:

```bash
cd ~/tg-bot
source venv/bin/activate
python setup_webhook.py
```

Должно вывести:
```
✅ Webhook установлен: https://username.pythonanywhere.com/webhook/secret
```

Проверь:
```bash
python setup_webhook.py info
```

---

## Шаг 7. Проверка

Открой своего бота в Telegram → `/start` → должен ответить!

---

## Обновление кода

Когда вносишь изменения локально:

```bash
# Локально
git add .
git commit -m "описание"
git push
```

На PythonAnywhere в консоли **Bash**:
```bash
cd ~/tg-bot
git pull
```

Затем на вкладке **Web** нажми **Reload**.

---

## Частые проблемы

### "Bot is running" не показывается

- Проверь Error log на вкладке **Web → Log files**
- Обычно это опечатка в пути или проблема с `.env`

### Бот не отвечает, хотя Web App работает

Проверь webhook:
```bash
python setup_webhook.py info
```

Если `pending_update_count` большой — значит updates накапливаются, но не обрабатываются. Смотри Error log.

### Ошибка "OSError: [Errno 101] Network is unreachable"

На бесплатном тарифе PythonAnywhere **ограничен исходящий интернет**. Но `api.telegram.org` в whitelist — для Telegram бота всё должно работать.

### CPU quota exceeded

На Beginner тарифе 100 секунд CPU/день. Это **много** для webhook бота — обработка одного сообщения = миллисекунды. Если всё равно превышается — значит где-то зависающий код.

---

## Возврат к polling режиму (локально)

Если хочешь снова тестировать локально:

```bash
python setup_webhook.py delete
python main.py
```

Без удаления webhook polling не сработает — Telegram отправляет updates только в одно место.

---

## Ограничения бесплатного тарифа

- ✅ Работает 24/7 (webhook не засыпает)
- ✅ HTTPS URL
- ✅ api.telegram.org доступен
- ❌ 512 MB диск (для твоего бота с запасом)
- ❌ 100 секунд CPU/день (webhook использует ~1-2 сек/день)
- ❌ Один Web App
- ❌ Поддомен `.pythonanywhere.com`

Для твоего бота этого **достаточно**.
