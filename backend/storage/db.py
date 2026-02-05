import os

# import libsql_experimental as libsql
from dotenv import load_dotenv

load_dotenv()

# TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL")
# TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")


# def get_connection():
#     return libsql.connect(TURSO_DATABASE_URL, auth_token=TURSO_AUTH_TOKEN)

import sqlite3

def get_connection():
    return sqlite3.connect("app.db")


def rows_to_dicts(cursor):
    """Convert cursor results to list of dicts using column names from description."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
