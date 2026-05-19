from pathlib import Path

import apply_flow
import profile_store
import tracker
from schemas import ApplicationPackage


def test_tracker_profile_and_application_logs_use_temp_database(
    tmp_path: Path,
    monkeypatch,
    demo_application_package: ApplicationPackage,
) -> None:
    db_path = tmp_path / "jobs.db"
    monkeypatch.setattr(tracker, "DB_PATH", db_path)
    monkeypatch.setattr(profile_store, "DB_PATH", db_path)

    generated_job_id = tracker.save_job(
        demo_application_package,
        notes="Generated job note.",
        job_url="https://example.com/generated",
    )
    searched_job_id = tracker.save_searched_job(
        title="Searched Python Developer",
        company="SearchCo",
        location="Remote",
        job_url="https://example.com/search",
        notes="Searched job note.",
    )

    jobs = tracker.get_all_jobs()
    assert len(jobs) == 2
    assert any(job["job_url"] == "https://example.com/generated" for job in jobs)

    profile_text = "Python SQL data analysis dashboards ETL pipelines stakeholder reporting. " * 3
    profile_id = profile_store.save_profile(
        "Demo Profile",
        "Demo Candidate",
        "Python Developer",
        "Berlin",
        profile_text,
    )
    assert profile_store.get_profile_by_id(profile_id)["candidate_name"] == "Demo Candidate"

    prep_log_id = apply_flow.create_application_log(
        job_id=searched_job_id,
        application_channel="Job portal",
        cv_ready=True,
        cover_letter_ready=False,
        certificates_ready=False,
        portfolio_link_included=False,
        linkedin_link_included=True,
        salary_expectation_added=False,
        availability_added=False,
        work_authorization_answered=False,
        reviewed_manually=False,
        submitted_manually=False,
        cv_file_note="Demo_CV.pdf",
        notes="Preparation only.",
    )
    prep_log = apply_flow.get_application_log_by_id(prep_log_id)
    assert prep_log is not None
    assert prep_log["date_logged"]
    assert not prep_log["date_applied"]
    assert prep_log["cv_file_note"] == "Demo_CV.pdf"

    searched_after_prep = next(job for job in tracker.get_all_jobs() if job["id"] == searched_job_id)
    assert searched_after_prep["status"] != "Applied"

    submitted_log_id = apply_flow.create_application_log(
        job_id=generated_job_id,
        application_channel="Email",
        cv_ready=True,
        cover_letter_ready=True,
        certificates_ready=False,
        portfolio_link_included=True,
        linkedin_link_included=True,
        salary_expectation_added=False,
        availability_added=True,
        work_authorization_answered=True,
        reviewed_manually=True,
        submitted_manually=True,
        follow_up_date="2026-06-01",
        notes="Submitted manually.",
    )
    submitted_log = apply_flow.get_application_log_by_id(submitted_log_id)
    assert submitted_log["date_applied"]
    generated_after_submit = next(job for job in tracker.get_all_jobs() if job["id"] == generated_job_id)
    assert generated_after_submit["status"] == "Applied"
    assert "Generated job note." in generated_after_submit["notes"]

    apply_flow.update_application_log_notes(submitted_log_id, "Updated log note.")
    assert apply_flow.get_application_log_by_id(submitted_log_id)["notes"] == "Updated log note."
    apply_flow.delete_application_log(prep_log_id)
    assert apply_flow.get_application_log_by_id(prep_log_id) is None
    assert any(job["id"] == searched_job_id for job in tracker.get_all_jobs())
