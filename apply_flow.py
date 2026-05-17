"""Controlled manual application flow logging for JobPilot Agent V12."""

from __future__ import annotations

import sqlite3
from datetime import date, datetime
from typing import Any

import tracker


def init_application_log_db() -> None:
    """Create the local application log table if it does not exist."""

    tracker.init_db()
    tracker.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(tracker.DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS application_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                application_channel TEXT NOT NULL,
                cv_ready INTEGER NOT NULL,
                cover_letter_ready INTEGER NOT NULL,
                certificates_ready INTEGER NOT NULL,
                portfolio_link_included INTEGER NOT NULL,
                linkedin_link_included INTEGER NOT NULL,
                salary_expectation_added INTEGER NOT NULL,
                availability_added INTEGER NOT NULL,
                work_authorization_answered INTEGER NOT NULL,
                reviewed_manually INTEGER NOT NULL,
                submitted_manually INTEGER NOT NULL,
                cv_file_note TEXT,
                cover_letter_file_note TEXT,
                certificates_note TEXT,
                optional_message_draft TEXT,
                date_logged TEXT NOT NULL,
                date_applied TEXT,
                follow_up_date TEXT,
                notes TEXT,
                FOREIGN KEY(job_id) REFERENCES jobs(id)
            )
            """
        )


def create_application_log(
    job_id: int,
    application_channel: str,
    cv_ready: bool,
    cover_letter_ready: bool,
    certificates_ready: bool,
    portfolio_link_included: bool,
    linkedin_link_included: bool,
    salary_expectation_added: bool,
    availability_added: bool,
    work_authorization_answered: bool,
    reviewed_manually: bool,
    submitted_manually: bool,
    cv_file_note: str = "",
    cover_letter_file_note: str = "",
    certificates_note: str = "",
    optional_message_draft: str = "",
    follow_up_date: str = "",
    notes: str = "",
) -> int:
    """Create an application log and update tracker status after manual submission."""

    if job_id <= 0:
        raise ValueError("Select a saved job before logging an application.")

    if submitted_manually and not reviewed_manually:
        raise ValueError("Review the application manually before logging a manual submission.")

    follow_up_date = _validate_optional_iso_date(follow_up_date, "follow-up date")
    today = date.today().isoformat()
    date_applied = today if submitted_manually else ""

    init_application_log_db()
    with sqlite3.connect(tracker.DB_PATH) as connection:
        cursor = connection.execute(
            """
            INSERT INTO application_logs (
                job_id,
                application_channel,
                cv_ready,
                cover_letter_ready,
                certificates_ready,
                portfolio_link_included,
                linkedin_link_included,
                salary_expectation_added,
                availability_added,
                work_authorization_answered,
                reviewed_manually,
                submitted_manually,
                cv_file_note,
                cover_letter_file_note,
                certificates_note,
                optional_message_draft,
                date_logged,
                date_applied,
                follow_up_date,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job_id,
                application_channel.strip() or "Other",
                _as_int(cv_ready),
                _as_int(cover_letter_ready),
                _as_int(certificates_ready),
                _as_int(portfolio_link_included),
                _as_int(linkedin_link_included),
                _as_int(salary_expectation_added),
                _as_int(availability_added),
                _as_int(work_authorization_answered),
                _as_int(reviewed_manually),
                _as_int(submitted_manually),
                cv_file_note.strip(),
                cover_letter_file_note.strip(),
                certificates_note.strip(),
                optional_message_draft.strip(),
                today,
                date_applied,
                follow_up_date,
                notes.strip(),
            ),
        )
        log_id = int(cursor.lastrowid)

    if submitted_manually:
        _mark_job_applied(job_id, log_id, today, application_channel)

    return log_id


def get_application_logs(job_id: int | None = None) -> list[dict[str, Any]]:
    """Return application logs, optionally filtered by saved job id."""

    init_application_log_db()
    with sqlite3.connect(tracker.DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        if job_id is None:
            rows = connection.execute(
                """
                SELECT *
                FROM application_logs
                ORDER BY date_logged DESC, id DESC
                """
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT *
                FROM application_logs
                WHERE job_id = ?
                ORDER BY date_logged DESC, id DESC
                """,
                (job_id,),
            ).fetchall()
        return [dict(row) for row in rows]


def get_application_log_by_id(log_id: int) -> dict[str, Any] | None:
    """Return one application log by id."""

    init_application_log_db()
    with sqlite3.connect(tracker.DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            "SELECT * FROM application_logs WHERE id = ?",
            (log_id,),
        ).fetchone()
        return dict(row) if row else None


def update_application_log_notes(log_id: int, notes: str) -> None:
    """Update notes on an application log without changing tracker notes."""

    init_application_log_db()
    with sqlite3.connect(tracker.DB_PATH) as connection:
        connection.execute(
            "UPDATE application_logs SET notes = ? WHERE id = ?",
            (notes.strip(), log_id),
        )


def delete_application_log(log_id: int) -> None:
    """Delete an application log without deleting the linked tracker job."""

    init_application_log_db()
    with sqlite3.connect(tracker.DB_PATH) as connection:
        connection.execute("DELETE FROM application_logs WHERE id = ?", (log_id,))


def build_application_message_draft(
    job: dict,
    profile: dict | None,
    application_channel: str,
    tone: str = "Professional",
) -> str:
    """Build a conservative, copy-only application message draft."""

    role = _first_non_empty(job.get("role_title"), job.get("title"), "[Role]")
    company = _first_non_empty(job.get("company_name"), job.get("company"), "[Company]")
    candidate_name = "[Your Name]"
    if profile:
        candidate_name = _first_non_empty(profile.get("candidate_name"), candidate_name)

    if tone == "Concise":
        greeting = "Dear Hiring Team,"
        body = (
            f"I am applying for the {role} position at {company}. "
            "I would be happy to discuss how my background aligns with the role."
        )
        closing = f"Kind regards,\n{candidate_name}"
    elif tone == "Friendly":
        greeting = "Hello Hiring Team,"
        body = (
            f"I am interested in the {role} position at {company}. "
            "Thank you for reviewing my application materials. "
            "I would welcome the opportunity to discuss the role further."
        )
        closing = f"Best regards,\n{candidate_name}"
    else:
        greeting = "Dear Hiring Team,"
        body = (
            f"I am applying for the {role} position at {company}. "
            "I would be happy to discuss how my background and motivation align with this role."
        )
        closing = f"Kind regards,\n{candidate_name}"

    if application_channel in {"LinkedIn message", "Recruiter message"}:
        return f"{greeting}\n\n{body}\n\n{closing}"

    return f"{greeting}\n\n{body}\n\n{closing}"


def _as_int(value: bool) -> int:
    """Convert a checkbox boolean into a SQLite-friendly integer."""

    return 1 if value else 0


def _validate_optional_iso_date(value: str, field_name: str) -> str:
    """Validate an optional YYYY-MM-DD date string."""

    cleaned = value.strip()
    if not cleaned:
        return ""

    try:
        datetime.strptime(cleaned, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(f"Invalid {field_name}. Use YYYY-MM-DD.") from exc

    return cleaned


def _first_non_empty(*values: Any) -> str:
    """Return the first non-empty string-like value."""

    for value in values:
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def _mark_job_applied(job_id: int, log_id: int, date_applied: str, channel: str) -> None:
    """Mark a tracker job as applied and append a small log reference."""

    jobs = tracker.get_all_jobs()
    job = next((item for item in jobs if int(item["id"]) == int(job_id)), None)
    existing_notes = job.get("notes", "") if job else ""
    reference = f"Application log #{log_id}: submitted manually on {date_applied} via {channel}."

    tracker.update_job_status(job_id, "Applied")
    with sqlite3.connect(tracker.DB_PATH) as connection:
        connection.execute(
            "UPDATE jobs SET date_applied = ? WHERE id = ?",
            (date_applied, job_id),
        )
    if reference not in existing_notes:
        combined_notes = f"{existing_notes.strip()}\n\n{reference}".strip()
        tracker.update_job_notes(job_id, combined_notes)
