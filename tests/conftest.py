from __future__ import annotations

import pytest

from schemas import (
    ATSAnalysis,
    ApplicationPackage,
    CVContent,
    ClaimsCheck,
    CoverLetter,
    InterviewPrep,
    JobInfo,
    MatchAnalysis,
    SkillEvidence,
)


@pytest.fixture
def demo_application_package() -> ApplicationPackage:
    evidence = SkillEvidence(skill="Python", status="strong", evidence="The profile lists Python.")
    return ApplicationPackage(
        job_info=JobInfo(
            company_name="DemoCo",
            role_title="Python Developer",
            location="Berlin",
            work_mode="Hybrid",
            seniority="Mid-level",
            role_summary="Build internal data tooling.",
            responsibilities=["Build Python tools", "Collaborate with data teams"],
            required_skills=["Python", "SQL"],
            nice_to_have_skills=["Docker"],
            language_requirements=["English"],
            visa_or_work_authorization_clues=[],
            deadline=None,
        ),
        match_analysis=MatchAnalysis(
            match_score=68,
            match_confidence="medium",
            strong_matches=[evidence],
            partial_matches=[],
            missing_or_weak_skills=[],
            transferable_skills=[],
            risk_areas=["Clarify deployment experience."],
            strongest_application_angle="Python data tooling experience.",
        ),
        cv_content=CVContent(
            tailored_profile_summary="Python developer focused on data tooling.",
            tailored_bullet_points=["Built Python-based data processing tools."],
            recommended_skills_ordering=["Python", "SQL"],
            relevant_project_suggestions=["Use a relevant data tooling project."],
        ),
        cover_letter=CoverLetter(draft="Dear Hiring Team,\n\nI am applying for this role."),
        ats_analysis=ATSAnalysis(
            supported_keywords=["Python"],
            missing_keywords=["FastAPI"],
            needs_clarification_keywords=["CI/CD"],
            keyword_improvement_suggestions=[
                "Only add these keywords to your CV if you have real experience with them."
            ],
            weak_bullet_point_suggestions=["Add measurable impact only where true."],
            overused_phrases=[],
            formatting_risks=["Avoid icons and complex graphics."],
        ),
        claims_check=ClaimsCheck(
            unsupported_claims=[],
            warnings=["No obvious unsupported factual claims found. Still review before using."],
            overall_integrity_status="clean",
        ),
        interview_prep=InterviewPrep(
            likely_questions=["Why this role?"],
            technical_questions=["Explain your Python experience."],
            behavioral_questions=["Tell us about collaboration."],
            gap_based_questions=["How would you approach FastAPI?"],
            project_explanation_prompts=["Explain the data tooling project."],
        ),
        recommended_next_action="Review the package manually before applying.",
    )
