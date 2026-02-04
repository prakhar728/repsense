import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from backend.storage.db import get_connection, rows_to_dicts


def _init_db() -> None:
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS user_csvs (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            csv_content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id TEXT PRIMARY KEY,
            profile_json TEXT NOT NULL,
            generated_at TEXT NOT NULL
        )
        """
    )
    conn.commit()


_init_db()


def save_csv(user_id: str, filename: str, csv_content: str) -> str:
    """
    Store an uploaded CSV in the database. Returns the generated CSV id.
    """
    csv_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    conn = get_connection()
    conn.execute(
        "INSERT INTO user_csvs (id, user_id, filename, csv_content, created_at) VALUES (?, ?, ?, ?, ?)",
        (csv_id, user_id, filename, csv_content, created_at),
    )
    conn.commit()
    return csv_id


def get_csv(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve the most recent CSV for a user.
    """
    conn = get_connection()
    cursor = conn.execute(
        "SELECT id, filename, csv_content, created_at FROM user_csvs WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
        (user_id,),
    )
    rows = rows_to_dicts(cursor)
    if not rows:
        return None
    return rows[0]


def save_profile(user_id: str, profile: Dict[str, Any]) -> None:
    """
    Store or replace a user's generated profile.
    """
    generated_at = datetime.utcnow().isoformat()
    conn = get_connection()
    conn.execute(
        """
        INSERT OR REPLACE INTO user_profiles (user_id, profile_json, generated_at)
        VALUES (?, ?, ?)
        """,
        (user_id, json.dumps(profile), generated_at),
    )
    conn.commit()


def get_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a user's profile.
    """
    conn = get_connection()
    cursor = conn.execute(
        "SELECT profile_json FROM user_profiles WHERE user_id = ?",
        (user_id,),
    )
    rows = rows_to_dicts(cursor)
    if not rows:
        return None
    return json.loads(rows[0]["profile_json"])
