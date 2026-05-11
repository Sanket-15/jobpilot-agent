"""Local SQLite candidate profile memory for JobPilot Agent V3."""

import sqlite3
from pathlib import Path
from typing import Any


DB_PATH = Path("data") / "jobs.db"
MIN_PROFILE_TEXT_CHARS = 120


def init_profile_db() -> None:
    """Create the local profiles table if needed."""

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_name TEXT NOT NULL UNIQUE,
                candidate_name TEXT,
                target_roles TEXT,
                preferred_locations TEXT,
                profile_text TEXT NOT NULL,
                date_created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                date_updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def _validate_profile(profile_name: str, profile_text: str) -> None:
    """Validate required profile fields before saving."""

    if not profile_name.strip():
        raise ValueError("Profile name is required.")

    if not profile_text.strip():
        raise ValueError("Profile text is required.")

    if len(profile_text.strip()) < MIN_PROFILE_TEXT_CHARS:
        raise ValueError("Profile text looks too short. Paste a fuller CV or candidate profile.")


def _profile_name_exists(connection: sqlite3.Connection, profile_name: str, profile_id: int | None = None) -> bool:
    """Return True when a profile name already exists, ignoring case."""

    if profile_id is None:
        row = connection.execute(
            "SELECT id FROM profiles WHERE lower(profile_name) = lower(?)",
            (profile_name.strip(),),
        ).fetchone()
    else:
        row = connection.execute(
            "SELECT id FROM profiles WHERE lower(profile_name) = lower(?) AND id != ?",
            (profile_name.strip(), profile_id),
        ).fetchone()

    return row is not None


def save_profile(
    profile_name: str,
    candidate_name: str,
    target_roles: str,
    preferred_locations: str,
    profile_text: str,
) -> int:
    """Save a new candidate profile and return its id."""

    _validate_profile(profile_name, profile_text)
    init_profile_db()

    with sqlite3.connect(DB_PATH) as connection:
        if _profile_name_exists(connection, profile_name):
            raise ValueError(
                "A profile with this name already exists. Select it below to edit it, or choose a different profile name."
            )

        try:
            cursor = connection.execute(
                """
                INSERT INTO profiles (
                    profile_name,
                    candidate_name,
                    target_roles,
                    preferred_locations,
                    profile_text
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    profile_name.strip(),
                    candidate_name.strip(),
                    target_roles.strip(),
                    preferred_locations.strip(),
                    profile_text.strip(),
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError(
                "A profile with this name already exists. Select it below to edit it, or choose a different profile name."
            ) from exc

        return int(cursor.lastrowid)


def get_all_profiles() -> list[dict[str, Any]]:
    """Return all saved candidate profiles as dictionaries."""

    init_profile_db()
    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT
                id,
                profile_name,
                candidate_name,
                target_roles,
                preferred_locations,
                profile_text,
                date_created,
                date_updated
            FROM profiles
            ORDER BY profile_name COLLATE NOCASE
            """
        ).fetchall()
        return [dict(row) for row in rows]


def get_profile_by_id(profile_id: int) -> dict[str, Any] | None:
    """Return one saved profile by id."""

    init_profile_db()
    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            """
            SELECT
                id,
                profile_name,
                candidate_name,
                target_roles,
                preferred_locations,
                profile_text,
                date_created,
                date_updated
            FROM profiles
            WHERE id = ?
            """,
            (profile_id,),
        ).fetchone()
        return dict(row) if row else None


def update_profile(
    profile_id: int,
    profile_name: str,
    candidate_name: str,
    target_roles: str,
    preferred_locations: str,
    profile_text: str,
) -> None:
    """Update an existing saved profile."""

    _validate_profile(profile_name, profile_text)
    init_profile_db()

    with sqlite3.connect(DB_PATH) as connection:
        if _profile_name_exists(connection, profile_name, profile_id=profile_id):
            raise ValueError(
                "A profile with this name already exists. Choose a unique profile name."
            )

        try:
            connection.execute(
                """
                UPDATE profiles
                SET
                    profile_name = ?,
                    candidate_name = ?,
                    target_roles = ?,
                    preferred_locations = ?,
                    profile_text = ?,
                    date_updated = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    profile_name.strip(),
                    candidate_name.strip(),
                    target_roles.strip(),
                    preferred_locations.strip(),
                    profile_text.strip(),
                    profile_id,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError(
                "A profile with this name already exists. Choose a unique profile name."
            ) from exc


def delete_profile(profile_id: int) -> None:
    """Delete a saved candidate profile."""

    init_profile_db()
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
