import json
import sqlite3
import uuid
from pathlib import Path
from typing import Optional, Dict, Any


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
            CREATE TABLE IF NOT EXISTS routines (
                id TEXT PRIMARY KEY,
                routine_json TEXT NOT NULL
            )
            """
        )
        conn.commit()


_init_db()


def save_routine(routine: Dict[str, Any]) -> str:
    """
    Persist a routine JSON payload and return its generated ID.
    """
    routine_id = str(uuid.uuid4())
    with _get_connection() as conn:
        conn.execute(
            "INSERT INTO routines (id, routine_json) VALUES (?, ?)",
            (routine_id, json.dumps(routine)),
        )
        conn.commit()
    return routine_id


def get_routine(routine_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a routine JSON payload by ID.
    """
    with _get_connection() as conn:
        cursor = conn.execute(
            "SELECT routine_json FROM routines WHERE id = ?", (routine_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return json.loads(row["routine_json"])

