import sqlite3
import os
from datetime import datetime

DB_PATH = os.getenv(
    "DATABASE_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "bot_data.db")
)

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Создаём директорию для БД если её нет
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            percentage REAL NOT NULL,
            level TEXT NOT NULL,
            grammar_score INTEGER DEFAULT 0,
            vocabulary_score INTEGER DEFAULT 0,
            reading_score INTEGER DEFAULT 0,
            grammar_total INTEGER DEFAULT 0,
            vocabulary_total INTEGER DEFAULT 0,
            reading_total INTEGER DEFAULT 0,
            duration_seconds INTEGER,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_result(user_id, username, score, total, percentage, level,
                grammar_score, vocabulary_score, reading_score,
                grammar_total, vocabulary_total, reading_total,
                duration_seconds):
    conn = get_connection()
    conn.execute(
        """INSERT INTO results
           (user_id, username, score, total, percentage, level,
            grammar_score, vocabulary_score, reading_score,
            grammar_total, vocabulary_total, reading_total,
            duration_seconds, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, username, score, total, percentage, level,
         grammar_score, vocabulary_score, reading_score,
         grammar_total, vocabulary_total, reading_total,
         duration_seconds, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_user_results(user_id, limit=10):
    conn = get_connection()
    rows = conn.execute(
        """SELECT * FROM results
           WHERE user_id = ?
           ORDER BY created_at DESC
           LIMIT ?""",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return rows

def get_user_best(user_id):
    conn = get_connection()
    row = conn.execute(
        """SELECT * FROM results
           WHERE user_id = ?
           ORDER BY percentage DESC
           LIMIT 1""",
        (user_id,)
    ).fetchone()
    conn.close()
    return row
