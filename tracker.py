"""Local SQLite job tracker for JobPilot Agent V2."""

import sqlite3
from pathlib import Path
from typing import Any

from schemas import ApplicationPackage


DB_PATH = Path("data") / "jobs.db"

ALLOWED_STATUSES = [
    "Interested",
    "Ready to apply",
    "Applied",
    "Interview scheduled",
    "Technical interview",
    "Rejected",
    "Offer",
    "Archived",
]


def init_db() -> None:
    """Create the local tracker database and jobs table if needed."""

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT,
                role_title TEXT,
                location TEXT,
                work_mode TEXT,
                match_score INTEGER,
                match_confidence TEXT,
                status TEXT NOT NULL,
                date_added TEXT NOT NULL DEFAULT CURRENT_DATE,
                date_applied TEXT,
                follow_up_date TEXT,
                recommended_next_action TEXT,
                notes TEXT
            )
            """
        )
        _ensure_job_url_column(connection)


def _ensure_job_url_column(connection: sqlite3.Connection) -> None:
    """Add the optional job_url column for existing V2 tracker databases."""

    columns = {
        row[1]
        for row in connection.execute("PRAGMA table_info(jobs)").fetchall()
    }
    if "job_url" not in columns:
        connection.execute("ALTER TABLE jobs ADD COLUMN job_url TEXT")


def save_job(
    application_package: ApplicationPackage,
    notes: str = "",
    job_url: str | None = None,
) -> int:
    """Save tracker-level metadata from an application package."""

    init_db()
    job = application_package.job_info
    match = application_package.match_analysis

    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute(
            """
            INSERT INTO jobs (
                company_name,
                role_title,
                location,
                work_mode,
                match_score,
                match_confidence,
                status,
                recommended_next_action,
                notes,
                job_url
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job.company_name,
                job.role_title,
                job.location,
                job.work_mode,
                match.match_score,
                match.match_confidence,
                "Interested",
                application_package.recommended_next_action,
                notes,
                job_url,
            ),
        )
        return int(cursor.lastrowid)


def save_searched_job(
    title: str,
    company: str,
    location: str | None = None,
    work_mode: str | None = None,
    job_url: str | None = None,
    notes: str = "",
    status: str = "Interested",
) -> int:
    """Save tracker metadata for a searched job without generating a package."""

    if status not in ALLOWED_STATUSES:
        raise ValueError(f"Unsupported status: {status}")

    init_db()
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute(
            """
            INSERT INTO jobs (
                company_name,
                role_title,
                location,
                work_mode,
                match_score,
                match_confidence,
                status,
                recommended_next_action,
                notes,
                job_url
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                company,
                title,
                location,
                work_mode,
                0,
                "not_scored",
                status,
                "Review the job details, then generate an application package if it looks relevant.",
                notes,
                job_url,
            ),
        )
        return int(cursor.lastrowid)


def get_all_jobs() -> list[dict[str, Any]]:
    """Return all saved tracker jobs as dictionaries."""

    init_db()
    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT
                id,
                company_name,
                role_title,
                location,
                work_mode,
                match_score,
                match_confidence,
                status,
                date_added,
                date_applied,
                follow_up_date,
                recommended_next_action,
                notes,
                job_url
            FROM jobs
            ORDER BY date_added DESC, id DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]


def update_job_status(job_id: int, status: str) -> None:
    """Update a saved job's application status."""

    if status not in ALLOWED_STATUSES:
        raise ValueError(f"Unsupported status: {status}")

    init_db()
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("UPDATE jobs SET status = ? WHERE id = ?", (status, job_id))


def update_job_notes(job_id: int, notes: str) -> None:
    """Update notes for a saved job."""

    init_db()
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("UPDATE jobs SET notes = ? WHERE id = ?", (notes, job_id))


def update_follow_up_date(job_id: int, follow_up_date: str) -> None:
    """Update the follow-up date for a saved job."""

    init_db()
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            "UPDATE jobs SET follow_up_date = ? WHERE id = ?",
            (follow_up_date, job_id),
        )


def delete_job(job_id: int) -> None:
    """Delete a saved job from the local tracker."""

    init_db()
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
