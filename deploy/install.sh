#!/bin/bash
# Установка бота на Ubuntu/Debian сервер через systemd
set -e

BOT_DIR="/opt/english-bot"
BOT_USER="botuser"

echo "=== Установка English Level Bot ==="

# 1. Создаём пользователя
if ! id -u $BOT_USER &>/dev/null; then
    sudo useradd -r -s /bin/false -m -d $BOT_DIR $BOT_USER
    echo "✓ Пользователь $BOT_USER создан"
fi

# 2. Копируем файлы
sudo mkdir -p $BOT_DIR/data $BOT_DIR/logs
sudo cp -r ./* $BOT_DIR/
sudo chown -R $BOT_USER:$BOT_USER $BOT_DIR

# 3. Создаём venv и ставим зависимости
sudo -u $BOT_USER python3 -m venv $BOT_DIR/venv
sudo -u $BOT_USER $BOT_DIR/venv/bin/pip install -r $BOT_DIR/requirements.txt
echo "✓ Зависимости установлены"

# 4. Проверяем .env
if [ ! -f $BOT_DIR/.env ]; then
    echo "⚠️  Создай файл $BOT_DIR/.env на основе .env.example"
    echo "   sudo cp $BOT_DIR/.env.example $BOT_DIR/.env"
    echo "   sudo nano $BOT_DIR/.env"
    exit 1
fi

# 5. Устанавливаем systemd unit
sudo cp $BOT_DIR/deploy/english-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable english-bot
sudo systemctl start english-bot

echo "✓ Бот запущен"
echo ""
echo "Управление:"
echo "  sudo systemctl status english-bot    # статус"
echo "  sudo systemctl restart english-bot   # перезапуск"
echo "  sudo journalctl -u english-bot -f    # логи"
