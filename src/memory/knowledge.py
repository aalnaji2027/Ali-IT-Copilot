import sqlite3
from pathlib import Path

DB_PATH = Path("data/database/copilot.db")


def save_document(
    file_name,
    file_path
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO knowledge
        (
            file_name,
            file_path
        )
        VALUES (?, ?)
        """,
        (
            file_name,
            file_path
        )
    )

    conn.commit()
    conn.close()


def get_documents():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            file_name,
            file_path
        FROM knowledge
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return rows