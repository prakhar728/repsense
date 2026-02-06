import json
import uuid
from typing import Optional, Dict, Any

from backend.storage.db import get_connection, rows_to_dicts


def _init_db() -> None:
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS routines (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            routine_json TEXT NOT NULL
        )
        """
    )
    conn.commit()


_init_db()


def save_routine(routine: Dict[str, Any], user_id: str) -> str:
    """
    Persist a routine JSON payload and return its generated ID.
    """
    routine_id = str(uuid.uuid4())
    conn = get_connection()
    conn.execute(
        "INSERT INTO routines (id, user_id, routine_json) VALUES (?, ?, ?)",
        (routine_id, user_id, json.dumps(routine)),
    )
    conn.commit()
    return routine_id


def get_routine(routine_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a routine JSON payload by ID, verifying it belongs to the user.
    """
    conn = get_connection()
    cursor = conn.execute(
        "SELECT routine_json FROM routines WHERE id = ? AND user_id = ?",
        (routine_id, user_id),
    )
    rows = rows_to_dicts(cursor)
    if not rows:
        return None
    return json.loads(rows[0]["routine_json"])
