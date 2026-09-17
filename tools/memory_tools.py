import sqlite3
from datetime import datetime
from pathlib import Path

DATABASE_PATH = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "agent.db"
        )

def initialise_database() -> None:
    """Create or update the memory database and tables if needed."""
    

    DATABASE_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
            )

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
                """
                CREATE TABLE IF NOT EXISTS project_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_name TEXT NOT NULL,
                    note TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    completed_at TEXT
                )
                """
                )

        columns = connection.execute(
                "PRAGMA table_info(project_notes)"
                ).fetchall()

        column_names = {
                column[1]
                for column in columns
                }

        if "completed_at" not in column_names:
            connection.execute(
                    """
                    ALTER TABLE project_notes
                    ADD COLUMN completed_at TEXT
                    """
                    )

def remember_project_note(
        project_name: str,
        note: str
        ) -> dict:
    """Store a note about one of the user's projects."""

    initialise_database()

    project_name = project_name.strip()
    note = note.strip()

    if not project_name:
        return {
                "success": False,
                "message": "Project name cannot be empty."
                }

    created_at = datetime.now().isoformat(
            timespec="seconds"
            )

    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.execute(
                """
                INSERT INTO project_notes (
                    project_name,
                    note,
                    created_at
                )
                VALUES (?, ?, ?)
                """,
                (
                    project_name,
                    note,
                    created_at,
                    )
                )

        note_id = cursor.lastrowid

    return {
            "success": True,
            "id": note_id,
            "project": project_name,
            "note": note,
            "created_at": created_at,
            }

def get_project_notes(
        project_name: str,
        limit: int = 10
        ) -> dict:
    """Return stored notes for a project"""

    initialise_database()

    limit = min(
            max(limit, 1),
            20
            )

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute(
                """
                SELECT
                    id,
                    note,
                    created_at
                FROM project_notes
                WHERE lower(project_name) = lower(?)
                AND completed_at IS NULL
                ORDER BY id DESC
                LIMIT ?
                """,

                (
                    project_name.strip(),
                    limit,
                    )
                ).fetchall()

        notes = [
                {
                    "id": row["id"],
                    "note": row["note"],
                    "created_at": row["created_at"],
                    }
                for row in rows
                ]
        return {
                "success": True,
                "project": project_name,
                "notes": notes,
                }

def complete_project_note(note_id: int) -> dict:
    """Mark a stored project note as completed."""

    initialise_database()

    completed_at = datetime.now().isoformat(
        timespec="seconds"
    )

    with sqlite3.connect(DATABASE_PATH) as connection:

        cursor = connection.execute(
            """
            UPDATE project_notes
            SET completed_at = ?
            WHERE id = ?
            AND completed_at IS NULL
            """,
            (
                completed_at,
                note_id,
            )
        )

        if cursor.rowcount == 0:
            return {
                "success": False,
                "message": (
                    f"Active note {note_id} was not found "
                    "or is already completed."
                )
            }

    return {
        "success": True,
        "id": note_id,
        "completed_at": completed_at,
        "message": f"Note {note_id} marked as completed."
    }
