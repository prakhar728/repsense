import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from typing import Optional

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "backend" / "storage" / "app.db"


def _get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db() -> None:
    with _get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id TEXT PRIMARY KEY,
                chat_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                routine_id TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


_init_db()


def ensure_chat_session(chat_id: str, user_id: str) -> None:
    """
    Ensure a chat session row exists for the given chat_id and user_id.
    """
    created_at = datetime.utcnow().isoformat()
    with _get_connection() as conn:
        cursor = conn.execute(
            "SELECT 1 FROM chat_sessions WHERE id = ?", (chat_id,)
        )
        if cursor.fetchone() is None:
            conn.execute(
                "INSERT INTO chat_sessions (id, user_id, created_at) VALUES (?, ?, ?)",
                (chat_id, user_id, created_at),
            )
            conn.commit()


def save_message(
    chat_id: str,
    role: str,
    content: str,
    routine_id: Optional[str] = None
) -> None:
    """
    Persist a single chat message.
    """
    message_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO chat_messages (id, chat_id, role, content, routine_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (message_id, chat_id, role, content, routine_id, created_at),
        )
        conn.commit()


def get_recent_messages(chat_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieve the most recent messages for a chat, ordered oldest-to-newest.
    """
    with _get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT role, content, routine_id, created_at
            FROM chat_messages
            WHERE chat_id = ?
            ORDER BY datetime(created_at) DESC
            LIMIT ?
            """,
            (chat_id, limit),
        )
        rows = cursor.fetchall()
        # Return in chronological order
        return [dict(row) for row in reversed(rows)]

