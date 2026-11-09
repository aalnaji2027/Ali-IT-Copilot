import sqlite3
from pathlib import Path


DB_PATH = Path("data/database/copilot.db")


def get_connection():
    """Return a configured SQLite connection."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_conversation_sessions():
    """Create and migrate the conversation-session schema."""
    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS conversation_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conversation_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(conversations)"
            ).fetchall()
        }

        if "session_id" not in conversation_columns:
            connection.execute(
                """
                ALTER TABLE conversations
                ADD COLUMN session_id INTEGER
                """
            )

        unassigned_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM conversations
            WHERE session_id IS NULL
            """
        ).fetchone()[0]

        if unassigned_count:
            cursor = connection.execute(
                """
                INSERT INTO conversation_sessions (title)
                VALUES (?)
                """,
                ("Imported History",),
            )

            imported_session_id = cursor.lastrowid

            connection.execute(
                """
                UPDATE conversations
                SET session_id = ?
                WHERE session_id IS NULL
                """,
                (imported_session_id,),
            )

        connection.commit()
    finally:
        connection.close()


def create_conversation_session(title="New Conversation"):
    """Create a conversation session and return its ID."""
    clean_title = str(title or "").strip() or "New Conversation"

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO conversation_sessions (title)
            VALUES (?)
            """,
            (clean_title,),
        )

        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def get_conversation_sessions():
    """Return conversation sessions, newest activity first."""
    initialize_conversation_sessions()
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                session.id,
                session.title,
                session.created_at,
                session.updated_at,
                COUNT(conversation.id) AS message_count
            FROM conversation_sessions AS session
            LEFT JOIN conversations AS conversation
                ON conversation.session_id = session.id
            GROUP BY
                session.id,
                session.title,
                session.created_at,
                session.updated_at
            ORDER BY
                session.updated_at DESC,
                session.id DESC
            """
        ).fetchall()

        return [dict(row) for row in rows]
    finally:
        connection.close()


def get_conversation_session(session_id):
    """Return one conversation session."""
    initialize_conversation_sessions()
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT
                id,
                title,
                created_at,
                updated_at
            FROM conversation_sessions
            WHERE id = ?
            """,
            (session_id,),
        ).fetchone()

        return dict(row) if row else None
    finally:
        connection.close()


def rename_conversation_session(session_id, title):
    """Rename an existing conversation session."""
    clean_title = str(title or "").strip()

    if not clean_title:
        return False

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE conversation_sessions
            SET
                title = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (clean_title, session_id),
        )

        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()


def delete_conversation_session(session_id):
    """Delete a session and all messages belonging to it."""
    connection = get_connection()

    try:
        connection.execute(
            """
            DELETE FROM conversations
            WHERE session_id = ?
            """,
            (session_id,),
        )

        cursor = connection.execute(
            """
            DELETE FROM conversation_sessions
            WHERE id = ?
            """,
            (session_id,),
        )

        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()


def save_conversation(
    user_message,
    assistant_response,
    session_id=None,
):
    """Save one user and assistant exchange."""
    initialize_conversation_sessions()

    if session_id is None:
        sessions = get_conversation_sessions()

        if sessions:
            session_id = sessions[0]["id"]
        else:
            session_id = create_conversation_session()

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO conversations (
                user_message,
                assistant_response,
                session_id
            )
            VALUES (?, ?, ?)
            """,
            (
                user_message,
                assistant_response,
                session_id,
            ),
        )

        connection.execute(
            """
            UPDATE conversation_sessions
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (session_id,),
        )

        connection.commit()
        return session_id
    finally:
        connection.close()


def get_conversations(limit=10, session_id=None):
    """Return conversation exchanges, newest first."""
    initialize_conversation_sessions()
    connection = get_connection()

    try:
        if session_id is None:
            rows = connection.execute(
                """
                SELECT
                    timestamp,
                    user_message,
                    assistant_response
                FROM conversations
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT
                    timestamp,
                    user_message,
                    assistant_response
                FROM conversations
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (session_id, limit),
            ).fetchall()

        return [
            (
                row["timestamp"],
                row["user_message"],
                row["assistant_response"],
            )
            for row in rows
        ]
    finally:
        connection.close()


def clear_conversations(session_id=None):
    """Clear one session or all conversation history."""
    connection = get_connection()

    try:
        if session_id is None:
            connection.execute(
                "DELETE FROM conversations"
            )

            connection.execute(
                "DELETE FROM conversation_sessions"
            )
        else:
            connection.execute(
                """
                DELETE FROM conversations
                WHERE session_id = ?
                """,
                (session_id,),
            )

            connection.execute(
                """
                UPDATE conversation_sessions
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (session_id,),
            )

        connection.commit()
    finally:
        connection.close()


initialize_conversation_sessions()
