import os
from dotenv import load_dotenv

load_dotenv()

import libsql_experimental as libsql
import certifi

TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")


def _connect():
    if not TURSO_DATABASE_URL:
        raise RuntimeError("TURSO_DATABASE_URL is not set.")
    if not os.getenv("SSL_CERT_FILE"):
        os.environ["SSL_CERT_FILE"] = certifi.where()
    return libsql.connect(TURSO_DATABASE_URL, auth_token=TURSO_AUTH_TOKEN)


class ReconnectingConnection:
    def __init__(self):
        self._conn = _connect()

    def _should_retry(self, exc: Exception) -> bool:
        message = str(exc)
        return "stream not found" in message or "Hrana" in message

    def execute(self, *args, **kwargs):
        try:
            return self._conn.execute(*args, **kwargs)
        except ValueError as exc:
            if not self._should_retry(exc):
                raise
            self._conn = _connect()
            return self._conn.execute(*args, **kwargs)

    def commit(self):
        try:
            return self._conn.commit()
        except ValueError as exc:
            if not self._should_retry(exc):
                raise
            self._conn = _connect()
            return self._conn.commit()

    def close(self):
        return self._conn.close()

    def __getattr__(self, name):
        return getattr(self._conn, name)


def get_connection():
    return ReconnectingConnection()


def rows_to_dicts(cursor):
    """Convert cursor results to list of dicts using column names from description."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
