import sqlite3
from contextlib import contextmanager

from app.config import DATABASE_PATH

# The provided database - its name is reused across queries.
TABLE_NAME = "offers"


# Open a read-only connection to the SQLite database, then close it afterwards.
@contextmanager
def get_db_connection():
    connection = sqlite3.connect(f"file:{DATABASE_PATH}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row

    try:
        yield connection
    finally:
        connection.close()


# Fetch all offer rows and convert them into JSON-friendly dictionaries.
def fetch_offers():
    with get_db_connection() as connection:
        rows = connection.execute(f"SELECT * FROM {TABLE_NAME}").fetchall()

    return [dict(row) for row in rows]


# Read the table's structure
def get_schema():
    with get_db_connection() as connection:
        columns = connection.execute(f"PRAGMA table_info({TABLE_NAME})").fetchall()

    return {
        "table": TABLE_NAME,
        "columns": [
            {"name": column["name"], "type": column["type"]} for column in columns
        ],
    }
