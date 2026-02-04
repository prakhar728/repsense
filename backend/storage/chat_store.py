import uuid
from datetime import datetime
from typing import List, Dict, Any
from typing import Optional

from backend.storage.db import get_connection, rows_to_dicts


def _init_db() -> None:
    conn = get_connection()
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
    conn = get_connection()
    cursor = conn.execute(
        "SELECT 1 FROM chat_sessions WHERE id = ?", (chat_id,)
    )
    if not cursor.fetchall():
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
    conn = get_connection()
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
    conn = get_connection()
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
    rows = rows_to_dicts(cursor)
    # Return in chronological order
    return list(reversed(rows))


def get_user_sessions(user_id: str) -> List[Dict[str, Any]]:
    """
    Return all chat sessions for a user, each with its most recent message.
    """
    conn = get_connection()
    cursor = conn.execute(
        """
        SELECT s.id, s.created_at,
               m.content AS last_message
        FROM chat_sessions s
        LEFT JOIN chat_messages m ON m.chat_id = s.id
            AND m.created_at = (
                SELECT MAX(m2.created_at) FROM chat_messages m2 WHERE m2.chat_id = s.id
            )
        WHERE s.user_id = ?
        ORDER BY s.created_at DESC
        """,
        (user_id,),
    )
    return rows_to_dicts(cursor)


def get_all_messages(chat_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve all messages for a chat session in chronological order.
    """
    conn = get_connection()
    cursor = conn.execute(
        """
        SELECT role, content, routine_id, created_at
        FROM chat_messages
        WHERE chat_id = ?
        ORDER BY datetime(created_at) ASC
        """,
        (chat_id,),
    )
    return rows_to_dicts(cursor)
