import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from backend.storage.db import get_connection, rows_to_dicts


def _init_db() -> None:
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS routines (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            routine_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    # Backfill missing created_at column if table already exists.
    cursor = conn.execute("PRAGMA table_info(routines)")
    columns = {row[1] for row in cursor.fetchall()}
    if "created_at" not in columns:
        conn.execute(
            "ALTER TABLE routines ADD COLUMN created_at TEXT NOT NULL DEFAULT (datetime('now'))"
        )
    conn.commit()


_init_db()


def save_routine(routine: Dict[str, Any], user_id: str) -> str:
    """
    Persist a routine JSON payload and return its generated ID.
    """
    routine_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    conn = get_connection()
    conn.execute(
        "INSERT INTO routines (id, user_id, routine_json, created_at) VALUES (?, ?, ?, ?)",
        (routine_id, user_id, json.dumps(routine), created_at),
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


def list_routines(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    List stored routines for a user (most recent first).
    """
    conn = get_connection()
    cursor = conn.execute(
        """
        SELECT id, routine_json, created_at
        FROM routines
        WHERE user_id = ?
        ORDER BY datetime(created_at) DESC
        LIMIT ?
        """,
        (user_id, limit),
    )
    rows = rows_to_dicts(cursor)
    routines = []
    for row in rows:
        routine_json = json.loads(row["routine_json"])
        routines.append({
            "id": row["id"],
            "created_at": row["created_at"],
            "routine": routine_json,
        })
    return routines
