"""Helper functions for JobPilot Agent."""

import json
import os
import re
from ast import literal_eval
from typing import Any

import google.generativeai as genai
from dotenv import load_dotenv
from pydantic import ValidationError

from prompts import build_application_prompt
from schemas import ApplicationPackage


DEFAULT_GEMINI_MODEL_NAME = "gemini-2.0-flash"
GEMINI_FALLBACK_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash-latest",
]
MIN_JOB_DESCRIPTION_CHARS = 120
MIN_CANDIDATE_PROFILE_CHARS = 120


class JobPilotError(Exception):
    """User-friendly error raised by the JobPilot workflow."""


def validate_inputs(job_description: str, candidate_profile: str) -> None:
    """Validate that both inputs contain enough information for a useful result."""

    if not job_description or not job_description.strip():
        raise JobPilotError("Please paste a job description before generating the package.")

    if not candidate_profile or not candidate_profile.strip():
        raise JobPilotError("Please paste a candidate profile or CV before generating the package.")

    if len(job_description.strip()) < MIN_JOB_DESCRIPTION_CHARS:
        raise JobPilotError(
            "The job description looks too short. Please paste the full posting or a more complete excerpt."
        )

    if len(candidate_profile.strip()) < MIN_CANDIDATE_PROFILE_CHARS:
        raise JobPilotError(
            "The candidate profile looks too short. Please paste a fuller CV, profile, or work history."
        )


def _get_api_key() -> str:
    """Load the Gemini API key from the environment."""

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise JobPilotError(
            "Missing GEMINI_API_KEY. Add it to your .env file or environment before running the app."
        )
    return api_key


def _get_model_names() -> list[str]:
    """Return the configured Gemini model followed by fallback models."""

    load_dotenv()
    configured_model = os.getenv("GEMINI_MODEL_NAME", DEFAULT_GEMINI_MODEL_NAME).strip()
    model_names = [configured_model]

    for fallback_model in GEMINI_FALLBACK_MODELS:
        if fallback_model not in model_names:
            model_names.append(fallback_model)

    return model_names


def call_gemini_json(job_description: str, candidate_profile: str) -> str:
    """Call Gemini and request valid JSON for the full application package."""

    api_key = _get_api_key()
    genai.configure(api_key=api_key)

    prompt = build_application_prompt(job_description, candidate_profile)
    last_error: Exception | None = None

    for model_name in _get_model_names():
        model = genai.GenerativeModel(
            model_name,
            generation_config={
                "temperature": 0.2,
                "response_mime_type": "application/json",
            },
        )

        try:
            response = model.generate_content(prompt)
            break
        except Exception as exc:
            last_error = exc
    else:
        raise JobPilotError(
            "Gemini API call failed for all configured models. "
            "Set GEMINI_MODEL_NAME in .env to a model available to your API key. "
            f"Last error: {last_error}"
        ) from last_error

    text = getattr(response, "text", None)
    if not text or not text.strip():
        raise JobPilotError("Gemini returned an empty response. Please try again.")

    return text.strip()


def parse_json_response(response_text: str) -> ApplicationPackage:
    """Parse Gemini JSON into the ApplicationPackage Pydantic model."""

    data = _load_json_leniently(response_text)

    try:
        return ApplicationPackage.model_validate(data)
    except ValidationError as exc:
        raise JobPilotError(f"Gemini JSON did not match the expected schema: {exc}") from exc


def _load_json_leniently(response_text: str) -> Any:
    """Load JSON while tolerating common model formatting mistakes."""

    candidates = [
        response_text,
        _extract_json_object(response_text) or "",
    ]

    repaired = [_repair_json_candidate(candidate) for candidate in candidates if candidate.strip()]
    candidates.extend(repaired)

    last_error: Exception | None = None
    for candidate in candidates:
        if not candidate.strip():
            continue
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as exc:
            last_error = exc

    for candidate in repaired:
        try:
            parsed = literal_eval(candidate)
            if isinstance(parsed, dict):
                return parsed
        except (SyntaxError, ValueError) as exc:
            last_error = exc

    if not candidates:
        raise JobPilotError(
            "Gemini returned invalid JSON. Please try again, or simplify the pasted text."
        )

    detail = f" Last parser error: {last_error}" if last_error else ""
    raise JobPilotError(
        "Gemini returned JSON-like text that could not be parsed. Please try again."
        + detail
    )


def _repair_json_candidate(text: str) -> str:
    """Apply conservative repairs for common JSON formatting issues."""

    repaired = text.strip()
    repaired = re.sub(r"^```(?:json)?", "", repaired, flags=re.IGNORECASE).strip()
    repaired = re.sub(r"```$", "", repaired).strip()
    repaired = repaired.replace("\u201c", '"').replace("\u201d", '"')
    repaired = repaired.replace("\u2018", "'").replace("\u2019", "'")
    repaired = re.sub(r",\s*([}\]])", r"\1", repaired)
    repaired = re.sub(r"\bNone\b", "null", repaired)
    repaired = re.sub(r"\bTrue\b", "true", repaired)
    repaired = re.sub(r"\bFalse\b", "false", repaired)
    return repaired


def _extract_json_object(text: str) -> str | None:
    """Extract the first JSON object from text, including markdown-fenced responses."""

    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    return text[start : end + 1]


def parse_job_description(package: ApplicationPackage) -> Any:
    """Return parsed job information from a generated package."""

    return package.job_info


def compare_profile_to_job(package: ApplicationPackage) -> Any:
    """Return the match analysis from a generated package."""

    return package.match_analysis


def calculate_match_score(package: ApplicationPackage) -> int:
    """Return the overall candidate-to-job match score."""

    return package.match_analysis.match_score


def create_tailored_cv_summary(package: ApplicationPackage) -> str:
    """Return the tailored CV profile summary."""

    return package.cv_content.tailored_profile_summary


def create_tailored_cv_bullets(package: ApplicationPackage) -> list[str]:
    """Return tailored CV bullet points."""

    return package.cv_content.tailored_bullet_points


def create_cover_letter(package: ApplicationPackage) -> str:
    """Return the generated cover letter draft."""

    return package.cover_letter.draft


def scan_resume_for_ats(package: ApplicationPackage) -> Any:
    """Return ATS and keyword analysis."""

    return package.ats_analysis


def generate_interview_questions(package: ApplicationPackage) -> Any:
    """Return interview preparation questions."""

    return package.interview_prep


def recommend_next_action(package: ApplicationPackage) -> str:
    """Return the recommended next action."""

    return package.recommended_next_action
