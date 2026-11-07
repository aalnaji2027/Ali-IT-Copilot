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

# =========================
# Knowledge Chunk Index
# =========================


def initialize_knowledge_chunks_table():
    """Create the table used to store indexed document chunks."""

    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge_chunks
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                sequence_number INTEGER NOT NULL,
                content TEXT NOT NULL,
                character_count INTEGER NOT NULL DEFAULT 0,
                word_count INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id)
                    REFERENCES knowledge (id)
                    ON DELETE CASCADE,
                UNIQUE (document_id, sequence_number)
            )
            """
        )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS
                idx_knowledge_chunks_document_id
            ON knowledge_chunks (document_id)
            """
        )

        conn.commit()


def index_document_chunks(document_id, chunks):
    """
    Replace the existing index for a document.

    Returns the number of chunks stored.
    """

    initialize_knowledge_chunks_table()

    if not chunks:
        return 0

    with get_connection() as conn:
        document = conn.execute(
            """
            SELECT id
            FROM knowledge
            WHERE id = ?
            """,
            (document_id,),
        ).fetchone()

        if document is None:
            raise ValueError(
                f"Knowledge document {document_id} "
                f"could not be found."
            )

        conn.execute(
            """
            DELETE FROM knowledge_chunks
            WHERE document_id = ?
            """,
            (document_id,),
        )

        chunk_records = []

        for chunk in chunks:
            content = chunk.get(
                "content",
                "",
            ).strip()

            if not content:
                continue

            chunk_records.append(
                (
                    document_id,
                    chunk["sequence_number"],
                    content,
                    chunk.get(
                        "character_count",
                        len(content),
                    ),
                    chunk.get(
                        "word_count",
                        len(content.split()),
                    ),
                )
            )

        conn.executemany(
            """
            INSERT INTO knowledge_chunks
            (
                document_id,
                sequence_number,
                content,
                character_count,
                word_count
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            chunk_records,
        )

        conn.commit()

    return len(chunk_records)


def get_document_chunk_count(document_id):
    """Return the number of indexed chunks for one document."""

    initialize_knowledge_chunks_table()

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT COUNT(*) AS chunk_count
            FROM knowledge_chunks
            WHERE document_id = ?
            """,
            (document_id,),
        ).fetchone()

    return row["chunk_count"]


def get_document_chunks(document_id):
    """Return all chunks for one document in sequence order."""

    initialize_knowledge_chunks_table()

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                id,
                document_id,
                sequence_number,
                content,
                character_count,
                word_count
            FROM knowledge_chunks
            WHERE document_id = ?
            ORDER BY sequence_number ASC
            """,
            (document_id,),
        ).fetchall()

    return [
        {
            "id": row["id"],
            "document_id": row["document_id"],
            "sequence_number": row["sequence_number"],
            "content": row["content"],
            "character_count": row["character_count"],
            "word_count": row["word_count"],
        }
        for row in rows
    ]


def search_knowledge_chunks(search_term, limit=10):
    """Search indexed chunks and include source information."""

    initialize_knowledge_chunks_table()

    clean_search_term = search_term.strip()

    if not clean_search_term:
        return []

    safe_limit = max(
        1,
        min(int(limit), 50),
    )

    search_pattern = (
        f"%{clean_search_term}%"
    )

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                knowledge_chunks.id AS chunk_id,
                knowledge_chunks.document_id,
                knowledge_chunks.sequence_number,
                knowledge_chunks.content,
                knowledge_chunks.character_count,
                knowledge_chunks.word_count,
                knowledge.file_name,
                knowledge.file_path
            FROM knowledge_chunks
            INNER JOIN knowledge
                ON knowledge.id =
                   knowledge_chunks.document_id
            WHERE
                knowledge_chunks.content
                    LIKE ? COLLATE NOCASE
                OR knowledge.file_name
                    LIKE ? COLLATE NOCASE
            ORDER BY
                knowledge_chunks.document_id DESC,
                knowledge_chunks.sequence_number ASC
            LIMIT ?
            """,
            (
                search_pattern,
                search_pattern,
                safe_limit,
            ),
        ).fetchall()

    return [
        {
            "chunk_id": row["chunk_id"],
            "document_id": row["document_id"],
            "sequence_number": row[
                "sequence_number"
            ],
            "content": row["content"],
            "character_count": row[
                "character_count"
            ],
            "word_count": row["word_count"],
            "file_name": row["file_name"],
            "file_path": row["file_path"],
        }
        for row in rows
    ]


def delete_document_chunks(document_id):
    """Delete all indexed chunks for one document."""

    initialize_knowledge_chunks_table()

    with get_connection() as conn:
        cursor = conn.execute(
            """
            DELETE FROM knowledge_chunks
            WHERE document_id = ?
            """,
            (document_id,),
        )

        deleted_count = cursor.rowcount
        conn.commit()

    return deleted_count


def get_index_statistics():
    """Return repository indexing statistics."""

    initialize_knowledge_chunks_table()

    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS total_chunks,
                COUNT(
                    DISTINCT document_id
                ) AS indexed_documents,
                COALESCE(
                    SUM(word_count),
                    0
                ) AS indexed_words
            FROM knowledge_chunks
            """
        ).fetchone()

    return {
        "total_chunks": row["total_chunks"],
        "indexed_documents": row[
            "indexed_documents"
        ],
        "indexed_words": row["indexed_words"],
    }


initialize_knowledge_chunks_table()