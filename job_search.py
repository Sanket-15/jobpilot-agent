"""Safe API/feed job search adapters for JobPilot Agent V10."""

import os
import re
from html import unescape
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from schemas import JobSearchResult
from skills import JobPilotError


REQUEST_TIMEOUT_SECONDS = 10
ADZUNA_COUNTRY = "de"
SOURCE_OPTIONS = ["All", "Adzuna", "Arbeitnow", "Remotive"]
LOCAL_ENV_PATH = Path(__file__).with_name(".env")


def _load_local_env() -> None:
    """Load environment variables from the project-local .env file."""

    load_dotenv(dotenv_path=LOCAL_ENV_PATH)


def adzuna_credentials_configured() -> bool:
    """Return True when Adzuna API credentials are available."""

    _load_local_env()
    return bool(os.getenv("ADZUNA_APP_ID") and os.getenv("ADZUNA_APP_KEY"))


def validate_job_search_inputs(query: str, max_results: int) -> None:
    """Validate user-provided search inputs."""

    if not query or not query.strip():
        raise JobPilotError("Please enter a job search keyword before searching.")

    if len(query.strip()) < 2:
        raise JobPilotError("The search query is too short. Use at least two characters.")

    if max_results < 1 or max_results > 50:
        raise JobPilotError("Max results must be between 1 and 50.")


def _clean_text(value: Any) -> str:
    """Clean plain text or simple HTML snippets from provider responses."""

    if value is None:
        return ""

    text = unescape(str(value))
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _contains_remote(text: str) -> bool:
    """Return True when text suggests a remote job."""

    lowered = text.lower()
    return any(term in lowered for term in ["remote", "home office", "work from home", "fully remote"])


def _salary_range(minimum: Any, maximum: Any, currency: str | None = None) -> str | None:
    """Format a salary range from provider fields."""

    parts = [str(value) for value in [minimum, maximum] if value not in (None, "")]
    if not parts:
        return None
    salary = " - ".join(parts)
    return f"{salary} {currency}".strip() if currency else salary


def normalize_adzuna_job(raw_job: dict) -> JobSearchResult:
    """Normalize one Adzuna job response."""

    company = raw_job.get("company") or {}
    location = raw_job.get("location") or {}
    category = raw_job.get("category") or {}
    area = location.get("area") if isinstance(location, dict) else None
    location_text = ", ".join(area) if isinstance(area, list) else _clean_text(location.get("display_name"))
    description = _clean_text(raw_job.get("description"))
    redirect_url = raw_job.get("redirect_url") or ""
    tags = [tag for tag in [_clean_text(category.get("label"))] if tag]

    return JobSearchResult(
        source="Adzuna",
        source_url=redirect_url,
        title=_clean_text(raw_job.get("title")) or "Untitled role",
        company=_clean_text(company.get("display_name")) or "Unknown company",
        location=location_text or None,
        remote=_contains_remote(f"{location_text} {description}"),
        job_type=_clean_text(raw_job.get("contract_time")) or _clean_text(raw_job.get("contract_type")) or None,
        salary=_salary_range(raw_job.get("salary_min"), raw_job.get("salary_max")),
        tags=tags,
        description=description,
        published_at=_clean_text(raw_job.get("created")) or None,
        apply_url=redirect_url or None,
    )


def normalize_arbeitnow_job(raw_job: dict) -> JobSearchResult:
    """Normalize one Arbeitnow job response."""

    description = _clean_text(raw_job.get("description"))
    tags = [
        _clean_text(tag)
        for tag in raw_job.get("tags", [])
        if _clean_text(tag)
    ]
    location = _clean_text(raw_job.get("location"))
    remote = bool(raw_job.get("remote")) or _contains_remote(f"{location} {description}")
    url = raw_job.get("url") or raw_job.get("slug") or ""

    return JobSearchResult(
        source="Arbeitnow",
        source_url=url,
        title=_clean_text(raw_job.get("title")) or "Untitled role",
        company=_clean_text(raw_job.get("company_name")) or "Unknown company",
        location=location or None,
        remote=remote,
        job_type=None,
        salary=None,
        tags=tags,
        description=description,
        published_at=_clean_text(raw_job.get("created_at")) or None,
        apply_url=url or None,
    )


def normalize_remotive_job(raw_job: dict) -> JobSearchResult:
    """Normalize one Remotive job response."""

    description = _clean_text(raw_job.get("description"))
    tags = [
        _clean_text(tag)
        for tag in raw_job.get("tags", [])
        if _clean_text(tag)
    ]
    category = _clean_text(raw_job.get("category"))
    if category and category not in tags:
        tags.append(category)
    url = raw_job.get("url") or ""

    return JobSearchResult(
        source="Remotive",
        source_url=url,
        title=_clean_text(raw_job.get("title")) or "Untitled role",
        company=_clean_text(raw_job.get("company_name")) or "Unknown company",
        location=_clean_text(raw_job.get("candidate_required_location")) or None,
        remote=True,
        job_type=_clean_text(raw_job.get("job_type")) or None,
        salary=_clean_text(raw_job.get("salary")) or None,
        tags=tags,
        description=description,
        published_at=_clean_text(raw_job.get("publication_date")) or None,
        apply_url=url or None,
    )


def _request_json(url: str, params: dict | None = None) -> dict:
    """Fetch provider JSON with simple error handling."""

    try:
        response = requests.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
            headers={"User-Agent": "JobPilotAgent/1.0 safe-job-search"},
        )
        response.raise_for_status()
        data = response.json()
    except requests.Timeout as exc:
        raise JobPilotError("Job search request timed out. Try again or use a different provider.") from exc
    except requests.RequestException as exc:
        raise JobPilotError(f"Job search API request failed: {exc}") from exc
    except ValueError as exc:
        raise JobPilotError("Job search provider returned invalid JSON.") from exc

    if not isinstance(data, dict):
        raise JobPilotError("Job search provider returned an unexpected response.")
    return data


def search_adzuna_jobs(
    query: str,
    location: str = "",
    remote_only: bool = False,
    max_results: int = 25,
) -> list[JobSearchResult]:
    """Search Adzuna when credentials are configured."""

    _load_local_env()
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        raise JobPilotError("Adzuna credentials are not configured. Using free providers only.")

    data = _request_json(
        f"https://api.adzuna.com/v1/api/jobs/{ADZUNA_COUNTRY}/search/1",
        params={
            "app_id": app_id,
            "app_key": app_key,
            "what": query,
            "where": location,
            "results_per_page": max_results,
            "content-type": "application/json",
        },
    )
    raw_jobs = data.get("results", [])
    if not isinstance(raw_jobs, list):
        raise JobPilotError("Adzuna returned an unexpected job list.")

    return filter_job_results(
        [normalize_adzuna_job(raw_job) for raw_job in raw_jobs if isinstance(raw_job, dict)],
        query=query,
        location=location,
        remote_only=remote_only,
    )[:max_results]


def search_arbeitnow_jobs(
    query: str,
    location: str = "",
    remote_only: bool = False,
    max_results: int = 25,
) -> list[JobSearchResult]:
    """Search Arbeitnow public feed and apply local filters."""

    data = _request_json("https://www.arbeitnow.com/api/job-board-api")
    raw_jobs = data.get("data", [])
    if not isinstance(raw_jobs, list):
        raise JobPilotError("Arbeitnow returned an unexpected job list.")

    jobs = [normalize_arbeitnow_job(raw_job) for raw_job in raw_jobs if isinstance(raw_job, dict)]
    return filter_job_results(jobs, query=query, location=location, remote_only=remote_only)[:max_results]


def search_remotive_jobs(
    query: str,
    location: str = "",
    remote_only: bool = False,
    max_results: int = 25,
) -> list[JobSearchResult]:
    """Search Remotive public remote jobs API and apply local filters."""

    data = _request_json("https://remotive.com/api/remote-jobs", params={"search": query})
    raw_jobs = data.get("jobs", [])
    if not isinstance(raw_jobs, list):
        raise JobPilotError("Remotive returned an unexpected job list.")

    jobs = [normalize_remotive_job(raw_job) for raw_job in raw_jobs if isinstance(raw_job, dict)]
    return filter_job_results(jobs, query=query, location=location, remote_only=remote_only)[:max_results]


def _matches_terms(job: JobSearchResult, terms: list[str], include_company: bool = True) -> bool:
    """Return True if all terms are found in searchable job text."""

    searchable_parts = [job.title, job.description, " ".join(job.tags)]
    if include_company:
        searchable_parts.append(job.company)
    searchable = " ".join(part or "" for part in searchable_parts).lower()
    return all(term.lower() in searchable for term in terms if term.strip())


def filter_job_results(
    jobs: list[JobSearchResult],
    query: str = "",
    location: str = "",
    remote_only: bool = False,
    skills_filter: str = "",
) -> list[JobSearchResult]:
    """Apply local keyword, location, remote, and skills filters."""

    filtered = jobs

    query_terms = [term for term in re.split(r"[\s,]+", query.strip()) if len(term) > 1]
    if query_terms:
        filtered = [job for job in filtered if _matches_terms(job, query_terms)]

    if location.strip():
        location_term = location.strip().lower()
        filtered = [
            job
            for job in filtered
            if location_term in ((job.location or "") + " " + job.description).lower()
        ]

    if remote_only:
        filtered = [
            job
            for job in filtered
            if job.remote is True or _contains_remote(f"{job.location or ''} {job.description}")
        ]

    skills = [term.strip() for term in skills_filter.split(",") if term.strip()]
    if skills:
        filtered = [job for job in filtered if _matches_terms(job, skills, include_company=False)]

    unique: list[JobSearchResult] = []
    seen: set[tuple[str, str, str]] = set()
    for job in filtered:
        key = (job.source, job.source_url or job.apply_url or "", job.title.lower())
        if key not in seen:
            seen.add(key)
            unique.append(job)

    return unique


def search_jobs(
    query: str,
    location: str = "",
    remote_only: bool = False,
    source: str = "All",
    skills_filter: str = "",
    max_results: int = 25,
) -> list[JobSearchResult]:
    """Search safe job APIs/feeds and return normalized filtered results."""

    validate_job_search_inputs(query, max_results)
    if source not in SOURCE_OPTIONS:
        raise JobPilotError(f"Unsupported job search source: {source}")

    providers = []
    if source in ("All", "Adzuna"):
        providers.append(search_adzuna_jobs)
    if source in ("All", "Arbeitnow"):
        providers.append(search_arbeitnow_jobs)
    if source in ("All", "Remotive"):
        providers.append(search_remotive_jobs)

    results: list[JobSearchResult] = []
    errors: list[str] = []
    for provider in providers:
        try:
            results.extend(provider(query, location, remote_only, max_results=max_results))
        except JobPilotError as exc:
            if source == "All" and "Adzuna credentials" in str(exc):
                continue
            errors.append(str(exc))

    if not results and errors:
        raise JobPilotError("; ".join(errors))

    return filter_job_results(
        results,
        query=query,
        location=location,
        remote_only=remote_only,
        skills_filter=skills_filter,
    )[:max_results]
