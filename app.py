"""Streamlit UI for JobPilot Agent."""

import streamlit as st

from agent import generate_application_package
from schemas import ApplicationPackage, SkillEvidence
from skills import JobPilotError


st.set_page_config(page_title="JobPilot Agent", page_icon="JP", layout="wide")


def render_list(items: list[str]) -> None:
    """Render a copy-friendly list."""

    if not items:
        st.write("No items detected.")
        return

    for item in items:
        st.markdown(f"- {item}")


def render_warning_list(items: list[str]) -> None:
    """Render concise warnings in a more scannable format."""

    if not items:
        st.write("No warnings detected.")
        return

    for item in items:
        st.warning(item)


def render_skill_evidence(items: list[SkillEvidence]) -> None:
    """Render skill evidence entries."""

    if not items:
        st.write("No items detected.")
        return

    for item in items:
        st.markdown(f"- **{item.skill}** ({item.status}): {item.evidence}")


def render_text_block(text: str) -> None:
    """Render long generated text in a copy-friendly text area."""

    st.text_area(
        label="Copy-friendly output",
        value=text or "Not provided.",
        height=260,
        label_visibility="collapsed",
    )


def render_package(package: ApplicationPackage) -> None:
    """Render all application package sections."""

    st.header("Job Summary")
    job = package.job_info
    st.write(f"**Company:** {job.company_name or 'Not provided'}")
    st.write(f"**Role:** {job.role_title or 'Not provided'}")
    st.write(f"**Location:** {job.location or 'Not provided'}")
    st.write(f"**Work mode:** {job.work_mode or 'Not provided'}")
    st.write(f"**Seniority:** {job.seniority or 'Not provided'}")
    st.write(f"**Deadline:** {job.deadline or 'Not provided'}")
    st.write("**Role summary:**")
    st.write(job.role_summary)

    with st.expander("Responsibilities", expanded=True):
        render_list(job.responsibilities)
    with st.expander("Required skills", expanded=True):
        render_list(job.required_skills)
    with st.expander("Nice-to-have skills"):
        render_list(job.nice_to_have_skills)
    with st.expander("Language and authorization clues"):
        st.write("**Language requirements:**")
        render_list(job.language_requirements)
        st.write("**Visa/work authorization clues:**")
        render_list(job.visa_or_work_authorization_clues)

    st.header("Match Analysis")
    match = package.match_analysis
    st.metric("Match score", f"{match.match_score}/100")
    st.write(f"**Confidence:** {match.match_confidence}")
    st.write(f"**Strongest application angle:** {match.strongest_application_angle}")

    with st.expander("Strong matches", expanded=True):
        render_skill_evidence(match.strong_matches)
    with st.expander("Partial matches", expanded=True):
        render_skill_evidence(match.partial_matches)
    with st.expander("Missing or weak skills", expanded=True):
        render_skill_evidence(match.missing_or_weak_skills)
    with st.expander("Transferable skills"):
        render_skill_evidence(match.transferable_skills)
    with st.expander("Risk areas", expanded=True):
        render_list(match.risk_areas)

    st.header("Tailored CV Summary")
    render_text_block(package.cv_content.tailored_profile_summary)

    st.header("Tailored CV Bullet Points")
    render_text_block("\n".join(f"- {item}" for item in package.cv_content.tailored_bullet_points))

    with st.expander("Recommended skills ordering", expanded=True):
        render_list(package.cv_content.recommended_skills_ordering)
    with st.expander("Relevant project suggestions"):
        render_list(
            package.cv_content.relevant_project_suggestions
            or [
                "Use the most relevant projects from the pasted candidate profile, such as an ML parking occupancy prediction project, fleet data analysis tool, CNN raw sensor data thesis, or computer vision projects with TensorFlow/OpenCV where these are actually present."
            ]
        )

    st.header("Cover Letter")
    render_text_block(package.cover_letter.draft)

    st.header("ATS / Keyword Suggestions")
    ats = package.ats_analysis
    st.subheader("Supported keywords")
    render_list(ats.supported_keywords)
    st.subheader("Missing keywords")
    render_list(ats.missing_keywords)
    if ats.missing_keywords:
        st.caption("Only add these keywords to your CV if you have real experience with them.")
    st.subheader("Needs clarification keywords")
    render_list(ats.needs_clarification_keywords)
    st.subheader("Keyword improvement suggestions")
    render_list(
        ats.keyword_improvement_suggestions
        or ["Use missing keywords as learning topics, interview preparation topics, or future upskilling areas."]
    )
    st.subheader("Weak bullet point suggestions")
    render_list(
        ats.weak_bullet_point_suggestions
        or ["No major weak bullet points detected in the generated version. Add measurable impact only where true."]
    )
    st.subheader("Overused phrases")
    render_list(ats.overused_phrases)
    st.subheader("Formatting risks")
    render_list(
        ats.formatting_risks
        or [
            "No major formatting risks detected from the pasted plain text. If using the original CV file, avoid icons, graphics, and non-standard language rating symbols for ATS compatibility."
        ]
    )

    st.header("Unsupported Claims Check")
    claims = package.claims_check
    if claims.overall_integrity_status == "clean":
        st.success(f"Integrity status: {claims.overall_integrity_status}")
    elif claims.overall_integrity_status == "needs_review":
        st.warning(f"Integrity status: {claims.overall_integrity_status}")
    else:
        st.error(f"Integrity status: {claims.overall_integrity_status}")

    st.subheader("Unsupported claims")
    render_warning_list(claims.unsupported_claims)
    st.subheader("Warnings")
    render_warning_list(claims.warnings)

    st.header("Interview Questions")
    interview = package.interview_prep
    st.subheader("Likely questions")
    render_list(interview.likely_questions)
    st.subheader("Technical questions")
    render_list(interview.technical_questions)
    st.subheader("Behavioral questions")
    render_list(interview.behavioral_questions)
    st.subheader("Gap-based questions")
    render_list(interview.gap_based_questions)
    st.subheader("Project explanation prompts")
    render_list(interview.project_explanation_prompts)

    st.header("Recommended Next Action")
    st.info(package.recommended_next_action)


st.title("JobPilot Agent")
st.write(
    "A local AI job-search assistant that helps turn a job description and candidate profile "
    "into a complete, reviewable application package."
)
st.warning(
    "Review all generated CV and cover letter content before using it. JobPilot should not invent "
    "experience, qualifications, companies, dates, tools, metrics, or achievements."
)

job_description = st.text_area(
    "Job description",
    height=260,
    placeholder="Paste the full job description here...",
)

candidate_profile = st.text_area(
    "Candidate profile / CV",
    height=260,
    placeholder="Paste the candidate profile, CV text, or work history here...",
)

if st.button("Generate Application Package", type="primary"):
    try:
        with st.spinner("Generating application package..."):
            result = generate_application_package(job_description, candidate_profile)
        render_package(result)
    except JobPilotError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(f"Something unexpected went wrong: {exc}")
