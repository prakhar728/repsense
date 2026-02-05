import json
import uuid
from datetime import datetime
from typing import List, Dict, Any

from backend.storage.db import get_connection, rows_to_dicts


def _init_db() -> None:
    """Initialize the episodic_memories table."""
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS episodic_memories (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            routine_id TEXT NOT NULL,
            outcome_type TEXT NOT NULL,
            outcome_text TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    # Create indexes
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_episodic_user_created 
        ON episodic_memories(user_id, created_at DESC)
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_episodic_routine 
        ON episodic_memories(routine_id)
        """
    )
    conn.commit()


_init_db()


def save_episode(
    user_id: str, routine_id: str, outcome_type: str, outcome_text: str
) -> str:
    """
    Persist an episodic memory entry.
    
    Args:
        user_id: User identifier
        routine_id: Routine identifier
        outcome_type: "positive", "negative", "injury", or "abandoned"
        outcome_text: Short verbatim user description
        
    Returns:
        Episode ID
    """
    episode_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO episodic_memories (id, user_id, routine_id, outcome_type, outcome_text, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (episode_id, user_id, routine_id, outcome_type, outcome_text, created_at),
    )
    conn.commit()
    return episode_id


def get_routine_candidates(user_id: str, days_back: int = 60) -> List[Dict[str, Any]]:
    """
    Get candidate routines for feedback resolution.
    
    Returns routines from the last N days with metadata.
    """
    conn = get_connection()
    cursor = conn.execute(
        """
        SELECT r.id, r.routine_json, 
               MAX(m.created_at) as last_mentioned_at,
               COUNT(DISTINCT e.id) as existing_outcomes
        FROM routines r
        JOIN chat_messages m ON m.routine_id = r.id
        JOIN chat_sessions s ON s.id = m.chat_id
        LEFT JOIN episodic_memories e ON e.routine_id = r.id AND e.user_id = ?
        WHERE s.user_id = ?
          AND m.created_at > datetime('now', '-' || ? || ' days')
        GROUP BY r.id
        ORDER BY MAX(m.created_at) DESC
        """,
        (user_id, user_id, days_back),
    )
    rows = rows_to_dicts(cursor)
    
    # Parse routine_json and add to result
    candidates = []
    for row in rows:
        try:
            routine_json = json.loads(row["routine_json"])
            candidates.append({
                "id": row["id"],
                "routine_json": routine_json,
                "last_mentioned_at": row["last_mentioned_at"],
                "existing_outcomes": row["existing_outcomes"],
            })
        except (json.JSONDecodeError, KeyError):
            continue
    
    return candidates




def get_episodes_by_user(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Retrieve episodic memories for a user (raw data, no interpretation).
    
    Returns list of episodes with routine JSON.
    """
    conn = get_connection()
    cursor = conn.execute(
        """
        SELECT e.id, e.routine_id, e.outcome_type, e.outcome_text, e.created_at, r.routine_json
        FROM episodic_memories e
        JOIN routines r ON r.id = e.routine_id
        WHERE e.user_id = ?
        ORDER BY e.created_at DESC
        LIMIT ?
        """,
        (user_id, limit),
    )
    rows = rows_to_dicts(cursor)
    
    episodes = []
    for row in rows:
        try:
            routine_json = json.loads(row["routine_json"])
            episodes.append({
                "routine_id": row["routine_id"],
                "routine_json": routine_json,
                "outcome_type": row["outcome_type"],
                "outcome_text": row["outcome_text"],
                "created_at": row["created_at"],
            })
        except (json.JSONDecodeError, KeyError):
            continue
    
    return episodes
