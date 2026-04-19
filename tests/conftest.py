import os
import sys
import tempfile
import pytest

# Добавляем корень проекта в path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def temp_db(monkeypatch):
    """Создаёт временную БД для каждого теста."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    monkeypatch.setenv("DATABASE_PATH", path)

    # Перезагружаем модуль database с новым путём
    import importlib
    from bot import database
    importlib.reload(database)
    database.init_db()

    yield database

    os.unlink(path)
