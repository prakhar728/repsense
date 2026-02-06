import os
from dotenv import load_dotenv

load_dotenv()

import libsql_experimental as libsql
import certifi

TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")


def get_connection():
    if not TURSO_DATABASE_URL:
        raise RuntimeError("TURSO_DATABASE_URL is not set.")
    if not os.getenv("SSL_CERT_FILE"):
        os.environ["SSL_CERT_FILE"] = certifi.where()
    return libsql.connect(TURSO_DATABASE_URL, auth_token=TURSO_AUTH_TOKEN)


def rows_to_dicts(cursor):
    """Convert cursor results to list of dicts using column names from description."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
