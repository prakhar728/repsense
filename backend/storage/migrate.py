import glob
import os
from datetime import datetime, timezone

from backend.storage.db import get_connection


MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), "migrations")


def _ensure_migrations_table(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id TEXT PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
        """
    )
    conn.commit()


def _get_applied_migrations(conn) -> set:
    cursor = conn.execute("SELECT id FROM schema_migrations")
    return {row[0] for row in cursor.fetchall()}


def _split_statements(sql: str) -> list:
    statements = []
    current = []
    for line in sql.splitlines():
        stripped = line.strip()
        if stripped.startswith("--") or stripped == "":
            continue
        current.append(line)
        if stripped.endswith(";"):
            statements.append("\n".join(current))
            current = []
    if current:
        statements.append("\n".join(current))
    return statements


def apply_migrations() -> None:
    conn = get_connection()
    _ensure_migrations_table(conn)
    applied = _get_applied_migrations(conn)

    migration_files = sorted(glob.glob(os.path.join(MIGRATIONS_DIR, "*.sql")))
    for path in migration_files:
        migration_id = os.path.basename(path)
        if migration_id in applied:
            continue
        with open(path, "r", encoding="utf-8") as f:
            sql = f.read()
        for statement in _split_statements(sql):
            conn.execute(statement)
        conn.execute(
            "INSERT INTO schema_migrations (id, applied_at) VALUES (?, ?)",
            (migration_id, datetime.now(timezone.utc).replace(microsecond=0).isoformat()),
        )
        conn.commit()


if __name__ == "__main__":
    apply_migrations()
