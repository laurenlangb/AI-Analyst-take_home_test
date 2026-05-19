import sqlite3
from contextlib import contextmanager

from app.config import DATABASE_PATH


# Open and close a connection to the SQLite database.
@contextmanager
def get_db_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    try:
        yield connection
    finally:
        connection.close()


# Fetch all offer rows and convert them into JSON-friendly dictionaries.
def fetch_offers():
    with get_db_connection() as connection:
        rows = connection.execute("SELECT * FROM offers").fetchall()

    return [dict(row) for row in rows]
