import sqlite3
from pathlib import Path

DB_PATH = Path("data/database/copilot.db")


def save_project(
    project_name,
    description,
    status
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO projects
        (
            project_name,
            description,
            status
        )
        VALUES (?, ?, ?)
        """,
        (
            project_name,
            description,
            status
        )
    )

    conn.commit()
    conn.close()


def get_projects():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            project_name,
            description,
            status
        FROM projects
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return rows