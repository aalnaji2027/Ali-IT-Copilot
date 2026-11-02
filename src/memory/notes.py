import sqlite3
from pathlib import Path

DB_PATH = Path("data/database/copilot.db")


def save_note(title, content):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO notes
        (title, content)
        VALUES (?, ?)
        """,
        (title, content)
    )

    conn.commit()
    conn.close()


def get_notes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id,
               title,
               content,
               created_date
        FROM notes
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return rows