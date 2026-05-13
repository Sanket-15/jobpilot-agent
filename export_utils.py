"""Export helpers for JobPilot Agent application packages."""

import re


def _text(value: object) -> str:
    """Return a display-safe string for optional values."""

    if value is None:
        return "Not provided"
    text = str(value).strip()
    return text if text else "Not provided"


def _markdown_list(items: list[str]) -> str:
    """Render a Markdown list with a safe fallback."""

    if not items:
        return "No items provided."
    return "\n".join(f"- {item}" for item in items)


def _text_list(items: list[str]) -> str:
    """Render a plain text list with a safe fallback."""

    if not items:
        return "No items provided."
    return "\n".join(f"- {item}" for item in items)


def _skill_evidence_markdown(items: list[object]) -> str:
    """Render skill evidence items as Markdown."""

    if not items:
        return "No items provided."
    return "\n".join(
        f"- **{_text(item.skill)}** ({_text(item.status)}): {_text(item.evidence)}"
        for item in items
    )


def _skill_evidence_text(items: list[object]) -> str:
    """Render skill evidence items as plain text."""

    if not items:
        return "No items provided."
    return "\n".join(
        f"- {_text(item.skill)} ({_text(item.status)}): {_text(item.evidence)}"
        for item in items
    )


def application_package_to_markdown(application_package) -> str:
    """Convert an application package to Markdown."""

    job = application_package.job_info
    match = application_package.match_analysis
    cv = application_package.cv_content
    cover_letter = application_package.cover_letter
    ats = application_package.ats_analysis
    claims = application_package.claims_check
    interview = application_package.interview_prep

    return f"""# JobPilot Application Package

## Job Summary

- **Company:** {_text(job.company_name)}
- **Role:** {_text(job.role_title)}
- **Location:** {_text(job.location)}
- **Work mode:** {_text(job.work_mode)}
- **Seniority:** {_text(job.seniority)}
- **Deadline:** {_text(job.deadline)}

**Role summary**

{_text(job.role_summary)}

**Responsibilities**

{_markdown_list(job.responsibilities)}

**Required skills**

{_markdown_list(job.required_skills)}

**Nice-to-have skills**

{_markdown_list(job.nice_to_have_skills)}

**Language requirements**

{_markdown_list(job.language_requirements)}

**Visa/work authorization clues**

{_markdown_list(job.visa_or_work_authorization_clues)}

## Match Analysis

- **Match score:** {match.match_score}/100
- **Confidence:** {_text(match.match_confidence)}
- **Strongest application angle:** {_text(match.strongest_application_angle)}

**Strong matches**

{_skill_evidence_markdown(match.strong_matches)}

**Partial matches**

{_skill_evidence_markdown(match.partial_matches)}

**Missing or weak skills**

{_skill_evidence_markdown(match.missing_or_weak_skills)}

**Transferable skills**

{_skill_evidence_markdown(match.transferable_skills)}

**Risk areas**

{_markdown_list(match.risk_areas)}

## Tailored CV Summary

{_text(cv.tailored_profile_summary)}

## Tailored CV Bullet Points

{_markdown_list(cv.tailored_bullet_points)}

**Recommended skills ordering**

{_markdown_list(cv.recommended_skills_ordering)}

**Relevant project suggestions**

{_markdown_list(cv.relevant_project_suggestions)}

## Cover Letter

{_text(cover_letter.draft)}

## ATS / Keyword Suggestions

**Supported keywords**

{_markdown_list(getattr(ats, "supported_keywords", []))}

**Missing keywords**

{_markdown_list(ats.missing_keywords)}

**Needs clarification keywords**

{_markdown_list(getattr(ats, "needs_clarification_keywords", []))}

**Keyword improvement suggestions**

{_markdown_list(ats.keyword_improvement_suggestions)}

**Weak bullet point suggestions**

{_markdown_list(ats.weak_bullet_point_suggestions)}

**Overused phrases**

{_markdown_list(ats.overused_phrases)}

**Formatting risks**

{_markdown_list(ats.formatting_risks)}

## Unsupported Claims Check

- **Integrity status:** {_text(claims.overall_integrity_status)}

**Unsupported claims**

{_markdown_list(claims.unsupported_claims)}

**Warnings**

{_markdown_list(claims.warnings)}

## Interview Questions

**Likely questions**

{_markdown_list(interview.likely_questions)}

**Technical questions**

{_markdown_list(interview.technical_questions)}

**Behavioral questions**

{_markdown_list(interview.behavioral_questions)}

**Gap-based questions**

{_markdown_list(interview.gap_based_questions)}

**Project explanation prompts**

{_markdown_list(interview.project_explanation_prompts)}

## Recommended Next Action

{_text(application_package.recommended_next_action)}
"""


def application_package_to_text(application_package) -> str:
    """Convert an application package to plain text."""

    job = application_package.job_info
    match = application_package.match_analysis
    cv = application_package.cv_content
    cover_letter = application_package.cover_letter
    ats = application_package.ats_analysis
    claims = application_package.claims_check
    interview = application_package.interview_prep

    return f"""JobPilot Application Package
============================

Job Summary
-----------
Company: {_text(job.company_name)}
Role: {_text(job.role_title)}
Location: {_text(job.location)}
Work mode: {_text(job.work_mode)}
Seniority: {_text(job.seniority)}
Deadline: {_text(job.deadline)}

Role summary:
{_text(job.role_summary)}

Responsibilities:
{_text_list(job.responsibilities)}

Required skills:
{_text_list(job.required_skills)}

Nice-to-have skills:
{_text_list(job.nice_to_have_skills)}

Language requirements:
{_text_list(job.language_requirements)}

Visa/work authorization clues:
{_text_list(job.visa_or_work_authorization_clues)}

Match Analysis
--------------
Match score: {match.match_score}/100
Confidence: {_text(match.match_confidence)}
Strongest application angle: {_text(match.strongest_application_angle)}

Strong matches:
{_skill_evidence_text(match.strong_matches)}

Partial matches:
{_skill_evidence_text(match.partial_matches)}

Missing or weak skills:
{_skill_evidence_text(match.missing_or_weak_skills)}

Transferable skills:
{_skill_evidence_text(match.transferable_skills)}

Risk areas:
{_text_list(match.risk_areas)}

Tailored CV Summary
-------------------
{_text(cv.tailored_profile_summary)}

Tailored CV Bullet Points
-------------------------
{_text_list(cv.tailored_bullet_points)}

Recommended skills ordering:
{_text_list(cv.recommended_skills_ordering)}

Relevant project suggestions:
{_text_list(cv.relevant_project_suggestions)}

Cover Letter
------------
{_text(cover_letter.draft)}

ATS / Keyword Suggestions
-------------------------
Supported keywords:
{_text_list(getattr(ats, "supported_keywords", []))}

Missing keywords:
{_text_list(ats.missing_keywords)}

Needs clarification keywords:
{_text_list(getattr(ats, "needs_clarification_keywords", []))}

Keyword improvement suggestions:
{_text_list(ats.keyword_improvement_suggestions)}

Weak bullet point suggestions:
{_text_list(ats.weak_bullet_point_suggestions)}

Overused phrases:
{_text_list(ats.overused_phrases)}

Formatting risks:
{_text_list(ats.formatting_risks)}

Unsupported Claims Check
------------------------
Integrity status: {_text(claims.overall_integrity_status)}

Unsupported claims:
{_text_list(claims.unsupported_claims)}

Warnings:
{_text_list(claims.warnings)}

Interview Questions
-------------------
Likely questions:
{_text_list(interview.likely_questions)}

Technical questions:
{_text_list(interview.technical_questions)}

Behavioral questions:
{_text_list(interview.behavioral_questions)}

Gap-based questions:
{_text_list(interview.gap_based_questions)}

Project explanation prompts:
{_text_list(interview.project_explanation_prompts)}

Recommended Next Action
-----------------------
{_text(application_package.recommended_next_action)}
"""


def create_safe_filename(company_name: str | None, role_title: str | None, extension: str) -> str:
    """Create a safe lowercase export filename."""

    clean_extension = extension.lower().lstrip(".")
    parts = [part for part in [company_name, role_title] if part and part.strip()]
    if not parts:
        return f"jobpilot_application_package.{clean_extension}"

    base = "_".join(parts).lower()
    base = re.sub(r"[^a-z0-9]+", "_", base)
    base = re.sub(r"_+", "_", base).strip("_")
    if not base:
        base = "application_package"

    return f"jobpilot_{base}.{clean_extension}"
