"""
db_connector.py — Слой доступа к данным (Data Access Layer).

Все обращения к SQLite проходят через этот класс.
Чтобы переключиться на ИРБИС 64, достаточно заменить импорт
в main.py на IrbisConnector — интерфейс идентичен.
"""

import sqlite3
import sys
import os
from typing import Optional

# Путь к БД относительно этого файла
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "library.db")


class DatabaseConnector:
    """Предоставляет методы поиска книг и работы с историей чата."""

    def _get_conn(self) -> sqlite3.Connection:
        """Открывает и возвращает соединение с БД."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    # ── Книги ─────────────────────────────────────────────────────────────────

    def search_by_title(self, title: str) -> list[dict]:
        """Ищет книги по вхождению подстроки в название (регистронезависимо)."""
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM books WHERE LOWER(title) LIKE LOWER(?)",
                (f"%{title}%",)
            ).fetchall()
        return [dict(r) for r in rows]

    def search_by_author(self, author: str) -> list[dict]:
        """Ищет книги по вхождению подстроки в имя автора."""
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM books WHERE LOWER(author) LIKE LOWER(?)",
                (f"%{author}%",)
            ).fetchall()
        return [dict(r) for r in rows]

    def get_book_by_id(self, book_id: int) -> Optional[dict]:
        """Возвращает полную запись книги по её ID."""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM books WHERE id = ?", (book_id,)
            ).fetchone()
        return dict(row) if row else None

    # ── FAQ ───────────────────────────────────────────────────────────────────

    def search_faq(self, query: str) -> Optional[dict]:
        """
        Ищет подходящий FAQ по ключевым словам.
        Возвращает первый подходящий вопрос/ответ или None.
        """
        query_lower = query.lower()
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM faq").fetchall()

        for row in rows:
            keywords = [kw.strip().lower() for kw in row["keywords"].split(",")]
            if any(kw in query_lower for kw in keywords):
                return dict(row)
        return None

    # ── История чата ──────────────────────────────────────────────────────────

    def save_message(self, session_id: str, role: str, message: str):
        """Сохраняет одно сообщение в историю чата."""
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO chat_history (session_id, role, message) VALUES (?,?,?)",
                (session_id, role, message)
            )
            conn.commit()

    def get_history(self, session_id: str, limit: int = 50) -> list[dict]:
        """Возвращает последние N сообщений из истории сессии."""
        with self._get_conn() as conn:
            rows = conn.execute(
                """SELECT role, message, timestamp
                   FROM chat_history
                   WHERE session_id = ?
                   ORDER BY timestamp DESC
                   LIMIT ?""",
                (session_id, limit)
            ).fetchall()
        return [dict(r) for r in reversed(rows)]

    def clear_history(self, session_id: str):
        """Удаляет историю чата для данной сессии."""
        with self._get_conn() as conn:
            conn.execute(
                "DELETE FROM chat_history WHERE session_id = ?", (session_id,)
            )
            conn.commit()
