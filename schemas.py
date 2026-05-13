"""Pydantic schemas for JobPilot Agent structured output."""

from typing import Literal

from pydantic import BaseModel, Field


class SkillEvidence(BaseModel):
    """Evidence for a skill match, gap, or transferable skill."""

    skill: str
    status: str
    evidence: str


class JobInfo(BaseModel):
    """Structured facts extracted from the job description."""

    company_name: str | None = None
    role_title: str | None = None
    location: str | None = None
    work_mode: str | None = None
    seniority: str | None = None
    role_summary: str
    responsibilities: list[str]
    required_skills: list[str]
    nice_to_have_skills: list[str]
    language_requirements: list[str]
    visa_or_work_authorization_clues: list[str]
    deadline: str | None = None


class MatchAnalysis(BaseModel):
    """Candidate-to-job match analysis."""

    match_score: int = Field(ge=0, le=100)
    match_confidence: Literal["high", "medium", "low"]
    strong_matches: list[SkillEvidence]
    partial_matches: list[SkillEvidence]
    missing_or_weak_skills: list[SkillEvidence]
    transferable_skills: list[SkillEvidence]
    risk_areas: list[str]
    strongest_application_angle: str


class CVContent(BaseModel):
    """Tailored CV content suggestions."""

    tailored_profile_summary: str
    tailored_bullet_points: list[str]
    recommended_skills_ordering: list[str]
    relevant_project_suggestions: list[str]


class CoverLetter(BaseModel):
    """Cover letter draft."""

    draft: str


class ATSAnalysis(BaseModel):
    """ATS and keyword suggestions."""

    supported_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str]
    needs_clarification_keywords: list[str] = Field(default_factory=list)
    keyword_improvement_suggestions: list[str]
    weak_bullet_point_suggestions: list[str]
    overused_phrases: list[str]
    formatting_risks: list[str]


class ATSScanResult(BaseModel):
    """Dedicated ATS resume scanner result."""

    ats_score: int = Field(ge=0, le=100)
    match_confidence: Literal["high", "medium", "low"]
    supported_keywords: list[str]
    missing_keywords: list[str]
    needs_clarification_keywords: list[str]
    keyword_improvement_suggestions: list[str]
    weak_bullet_point_suggestions: list[str]
    formatting_risks: list[str]
    overused_phrases: list[str]
    suggested_skills_ordering: list[str]
    top_cv_improvements: list[str]
    unsupported_or_risky_claims: list[str]
    recommended_next_action: str


class NormalizedProfile(BaseModel):
    """Clean reusable candidate profile produced by the profile normalizer."""

    candidate_name: str | None = None
    suggested_profile_name: str
    target_roles: list[str]
    preferred_locations: list[str]
    professional_summary: str
    skills: list[str]
    tools_and_technologies: list[str]
    experience_summary: list[str]
    education: list[str]
    certifications: list[str]
    projects: list[str]
    languages: list[str]
    missing_or_unclear_information: list[str]
    warnings: list[str]
    normalized_profile_text: str


class ClaimsCheck(BaseModel):
    """Unsupported claim warnings."""

    unsupported_claims: list[str]
    warnings: list[str]
    overall_integrity_status: Literal["clean", "needs_review", "high_risk"]


class InterviewPrep(BaseModel):
    """Interview preparation questions."""

    likely_questions: list[str]
    technical_questions: list[str]
    behavioral_questions: list[str]
    gap_based_questions: list[str]
    project_explanation_prompts: list[str]


class ApplicationPackage(BaseModel):
    """Complete application package returned by JobPilot Agent."""

    job_info: JobInfo
    match_analysis: MatchAnalysis
    cv_content: CVContent
    cover_letter: CoverLetter
    ats_analysis: ATSAnalysis
    claims_check: ClaimsCheck
    interview_prep: InterviewPrep
    recommended_next_action: str
