import sqlite3
from datetime import datetime
from pathlib import Path

DATABASE_PATH = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "agent.db"
        )

def initialise_database() -> None:
    """Create the memory database and tables if needed."""

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
                    created_at TEXT NOT NULL
                )
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
