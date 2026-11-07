import sqlite3
from pathlib import Path


DB_PATH = Path("data/database/copilot.db")


def get_connection():
    """Create the database directory and return a connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    return conn


def initialize_knowledge_table():
    """Create the knowledge table if it does not already exist."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def save_document(file_name, file_path):
    """Save a document unless the same file path already exists."""
    initialize_knowledge_table()

    with get_connection() as conn:
        existing_document = conn.execute(
            """
            SELECT id
            FROM knowledge
            WHERE file_path = ?
            """,
            (str(file_path),),
        ).fetchone()

        if existing_document:
            return False

        conn.execute(
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
                str(file_path),
            ),
        )

        conn.commit()

    return True


def get_documents():
    """Return all saved documents, newest first."""
    initialize_knowledge_table()

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                id,
                file_name,
                file_path
            FROM knowledge
            ORDER BY id DESC
            """
        ).fetchall()

    return [
        (
            row["id"],
            row["file_name"],
            row["file_path"],
        )
        for row in rows
    ]


def search_documents(search_term):
    """Search document names and paths."""
    initialize_knowledge_table()

    search_term = search_term.strip()

    if not search_term:
        return get_documents()

    search_pattern = f"%{search_term}%"

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                id,
                file_name,
                file_path
            FROM knowledge
            WHERE
                file_name LIKE ? COLLATE NOCASE
                OR file_path LIKE ? COLLATE NOCASE
            ORDER BY id DESC
            """,
            (
                search_pattern,
                search_pattern,
            ),
        ).fetchall()

    return [
        (
            row["id"],
            row["file_name"],
            row["file_path"],
        )
        for row in rows
    ]


def get_document_statistics():
    """Return basic statistics about the knowledge repository."""
    initialize_knowledge_table()

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS total_documents,
                COUNT(DISTINCT file_name) AS unique_file_names
            FROM knowledge
            """
        ).fetchone()

    return {
        "total_documents": row["total_documents"],
        "unique_file_names": row["unique_file_names"],
    }


def delete_document(document_id):
    """Delete one document record and return its saved file path."""
    initialize_knowledge_table()

    with get_connection() as conn:
        document = conn.execute(
            """
            SELECT file_path
            FROM knowledge
            WHERE id = ?
            """,
            (document_id,),
        ).fetchone()

        if document is None:
            return None

        conn.execute(
            """
            DELETE FROM knowledge
            WHERE id = ?
            """,
            (document_id,),
        )

        conn.commit()

    return document["file_path"]


initialize_knowledge_table()