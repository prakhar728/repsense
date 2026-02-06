from backend.storage.db import get_connection
from backend.storage.migrate import apply_migrations


DROP_STATEMENTS = [
    "DROP INDEX IF EXISTS idx_messages_routine_user",
    "DROP INDEX IF EXISTS idx_episodic_user_created",
    "DROP INDEX IF EXISTS idx_episodic_routine",
    "DROP TABLE IF EXISTS chat_messages",
    "DROP TABLE IF EXISTS chat_sessions",
    "DROP TABLE IF EXISTS episodic_memories",
    "DROP TABLE IF EXISTS routines",
    "DROP TABLE IF EXISTS user_csvs",
    "DROP TABLE IF EXISTS user_profiles",
    "DROP TABLE IF EXISTS schema_migrations",
]


def reset_database() -> None:
    conn = get_connection()
    for statement in DROP_STATEMENTS:
        conn.execute(statement)
    conn.commit()
    apply_migrations()


if __name__ == "__main__":
    reset_database()
