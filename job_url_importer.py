"""Single URL job posting import for JobPilot Agent V8."""

import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from schemas import JobUrlImportResult
from skills import JobPilotError


REQUEST_TIMEOUT_SECONDS = 10
MAX_DOWNLOAD_BYTES = 1_500_000
MIN_EXTRACTED_CHARS = 500
PARTIAL_EXTRACTED_CHARS = 1200
USER_AGENT = "JobPilotAgent/1.0 single-url manual-review importer"

NOISE_PATTERNS = [
    "cookie",
    "privacy policy",
    "terms of use",
    "all rights reserved",
    "download our app",
    "other users also viewed",
    "recommended jobs",
    "similar jobs",
    "job alert",
    "share this job",
    "follow us",
    "subscribe",
    "sign in",
    "log in",
]

BLOCKED_PATTERNS = [
    "captcha",
    "access denied",
    "enable javascript",
    "please enable javascript",
    "sign in to view",
    "login to view",
    "unusual traffic",
]


def validate_job_url(url: str) -> None:
    """Validate a user-provided job posting URL."""

    if not url or not url.strip():
        raise JobPilotError("Please paste a job posting URL before importing.")

    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"}:
        raise JobPilotError("Please use a valid http or https job posting URL.")

    if not parsed.netloc:
        raise JobPilotError("The URL looks incomplete. Please paste the full job posting URL.")


def fetch_job_page(url: str) -> str:
    """Fetch one user-provided job posting page with conservative limits."""

    validate_job_url(url)
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"}

    try:
        with requests.get(
            url.strip(),
            headers=headers,
            timeout=REQUEST_TIMEOUT_SECONDS,
            stream=True,
        ) as response:
            response.raise_for_status()

            content_type = response.headers.get("content-type", "").lower()
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                raise JobPilotError(
                    "This URL did not return a normal HTML page. Please paste the job description manually."
                )

            chunks: list[bytes] = []
            downloaded = 0
            for chunk in response.iter_content(chunk_size=16384):
                if not chunk:
                    continue
                downloaded += len(chunk)
                if downloaded > MAX_DOWNLOAD_BYTES:
                    break
                chunks.append(chunk)

            encoding = response.encoding or "utf-8"
            return b"".join(chunks).decode(encoding, errors="replace")
    except requests.Timeout as exc:
        raise JobPilotError(
            "The job page request timed out. Please paste the job description manually."
        ) from exc
    except requests.RequestException as exc:
        raise JobPilotError(
            f"Could not fetch this job posting automatically. Please paste the job description manually. Details: {exc}"
        ) from exc


def extract_job_text_from_html(html: str) -> str:
    """Extract likely job posting text from HTML."""

    if not html or not html.strip():
        return ""

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg", "iframe", "form", "button"]):
        tag.decompose()

    for selector in [
        "nav",
        "header",
        "footer",
        "aside",
        "[class*='cookie']",
        "[id*='cookie']",
        "[class*='footer']",
        "[id*='footer']",
        "[class*='recommend']",
        "[id*='recommend']",
        "[class*='similar']",
        "[id*='similar']",
        "[class*='advert']",
        "[id*='advert']",
        "[class*='social']",
        "[id*='social']",
    ]:
        for element in soup.select(selector):
            element.decompose()

    candidates = soup.select(
        "main, article, [class*='job'], [id*='job'], [class*='description'], "
        "[id*='description'], [class*='posting'], [id*='posting']"
    )
    candidate_texts = [
        element.get_text(separator="\n", strip=True)
        for element in candidates
        if len(element.get_text(" ", strip=True)) > 200
    ]

    if candidate_texts:
        candidate_texts.sort(key=len, reverse=True)
        return "\n".join(candidate_texts[:3])

    return soup.get_text(separator="\n", strip=True)


def clean_extracted_job_text(text: str) -> str:
    """Clean extracted job text while preserving reviewable posting content."""

    if not text:
        return ""

    cleaned_lines: list[str] = []
    seen: set[str] = set()

    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        if not line:
            continue

        lower_line = line.lower()
        if len(line) <= 2:
            continue
        if any(pattern in lower_line for pattern in NOISE_PATTERNS):
            continue
        if lower_line in seen:
            continue

        seen.add(lower_line)
        cleaned_lines.append(line)

    cleaned = "\n".join(cleaned_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def import_job_from_url(url: str) -> JobUrlImportResult:
    """Import likely job description text from one user-provided URL."""

    validate_job_url(url)
    warnings: list[str] = []

    html = fetch_job_page(url)
    html_lower = html.lower()
    if any(pattern in html_lower for pattern in BLOCKED_PATTERNS):
        warnings.append(
            "The page may be blocked, login-only, CAPTCHA-protected, or JavaScript-rendered."
        )

    extracted = clean_extracted_job_text(extract_job_text_from_html(html))

    if not extracted:
        return JobUrlImportResult(
            source_url=url.strip(),
            extracted_text="",
            extraction_status="failed",
            warnings=warnings
            + ["Could not extract this job posting automatically. Please paste the job description manually."],
        )

    if len(extracted) < MIN_EXTRACTED_CHARS:
        return JobUrlImportResult(
            source_url=url.strip(),
            extracted_text=extracted,
            extraction_status="failed",
            warnings=warnings
            + ["The extracted text is too short to be reliable. Please paste the job description manually."],
        )

    status = "success"
    if warnings or len(extracted) < PARTIAL_EXTRACTED_CHARS:
        status = "partial"
        warnings.append("The extraction may be incomplete. Review and edit the text before generating.")

    return JobUrlImportResult(
        source_url=url.strip(),
        extracted_text=extracted,
        extraction_status=status,
        warnings=warnings,
    )
