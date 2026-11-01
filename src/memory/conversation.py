import sqlite3
from pathlib import Path

DB_PATH = Path("data/database/copilot.db")


def save_conversation(user_message, assistant_response):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO conversations
        (user_message, assistant_response)
        VALUES (?, ?)
        """,
        (user_message, assistant_response)
    )

    conn.commit()
    conn.close()


def get_conversations(limit=10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT timestamp,
               user_message,
               assistant_response
        FROM conversations
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )

    rows = cursor.fetchall()

    conn.close()

    return rows

def clear_conversations():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM conversations"
    )

    conn.commit()
    conn.close()