import pytest

import job_search
from schemas import JobSearchResult
from skills import JobPilotError


def test_provider_normalization_preserves_source_and_urls() -> None:
    adzuna = job_search.normalize_adzuna_job(
        {
            "title": "Python Developer",
            "company": {"display_name": "DemoCo"},
            "location": {"area": ["Germany", "Berlin"]},
            "description": "Build Python tools.",
            "redirect_url": "https://example.com/adzuna",
            "category": {"label": "IT"},
        }
    )
    arbeitnow = job_search.normalize_arbeitnow_job(
        {
            "title": "Data Analyst",
            "company_name": "ArbeitCo",
            "location": "Berlin",
            "description": "SQL dashboards.",
            "tags": ["SQL"],
            "url": "https://example.com/arbeitnow",
        }
    )
    remotive = job_search.normalize_remotive_job(
        {
            "title": "Remote ML Engineer",
            "company_name": "RemoteCo",
            "candidate_required_location": "Worldwide",
            "description": "Python machine learning.",
            "tags": ["Python"],
            "url": "https://example.com/remotive",
            "category": "Software",
        }
    )

    assert adzuna.source == "Adzuna"
    assert arbeitnow.source == "Arbeitnow"
    assert remotive.source == "Remotive"
    assert adzuna.apply_url == "https://example.com/adzuna"
    assert remotive.remote is True


def test_filter_job_results_by_query_remote_and_skills() -> None:
    jobs = [
        JobSearchResult(
            source="Remotive",
            source_url="https://example.com/1",
            title="Remote Python Developer",
            company="DemoCo",
            location="Remote",
            remote=True,
            job_type=None,
            salary=None,
            tags=["Python", "SQL"],
            description="Build Python and SQL data tools.",
            published_at=None,
            apply_url="https://example.com/1",
        ),
        JobSearchResult(
            source="Arbeitnow",
            source_url="https://example.com/2",
            title="Office Designer",
            company="DesignCo",
            location="Berlin",
            remote=False,
            job_type=None,
            salary=None,
            tags=["Figma"],
            description="Office role.",
            published_at=None,
            apply_url="https://example.com/2",
        ),
    ]

    filtered = job_search.filter_job_results(
        jobs,
        query="Python",
        remote_only=True,
        skills_filter="SQL",
    )

    assert len(filtered) == 1
    assert filtered[0].title == "Remote Python Developer"


def test_search_jobs_skips_missing_adzuna_credentials_for_all(monkeypatch: pytest.MonkeyPatch) -> None:
    def missing_adzuna(*args, **kwargs):
        raise JobPilotError("Adzuna credentials are not configured. Using free providers only.")

    def fake_arbeitnow(*args, **kwargs):
        return [
            JobSearchResult(
                source="Arbeitnow",
                source_url="https://example.com/job",
                title="Python Data Analyst",
                company="DemoCo",
                location="Berlin",
                remote=False,
                job_type=None,
                salary=None,
                tags=["Python"],
                description="Python analysis role.",
                published_at=None,
                apply_url="https://example.com/job",
            )
        ]

    monkeypatch.setattr(job_search, "search_adzuna_jobs", missing_adzuna)
    monkeypatch.setattr(job_search, "search_arbeitnow_jobs", fake_arbeitnow)
    monkeypatch.setattr(job_search, "search_remotive_jobs", lambda *args, **kwargs: [])

    results = job_search.search_jobs("Python", source="All")

    assert len(results) == 1
    assert results[0].source == "Arbeitnow"
