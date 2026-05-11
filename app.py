"""Streamlit UI for JobPilot Agent."""

import streamlit as st

from agent import generate_application_package
from profile_store import (
    delete_profile,
    get_all_profiles,
    get_profile_by_id,
    init_profile_db,
    save_profile,
    update_profile,
)
from schemas import ApplicationPackage, SkillEvidence
from skills import JobPilotError
from tracker import (
    ALLOWED_STATUSES,
    delete_job,
    get_all_jobs,
    init_db,
    save_job,
    update_follow_up_date,
    update_job_notes,
    update_job_status,
)


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


def render_save_to_tracker(package: ApplicationPackage) -> None:
    """Render controls for saving the generated package to the local tracker."""

    st.header("Save to Job Tracker")
    notes = st.text_area(
        "Tracker notes",
        key="tracker_save_notes",
        placeholder="Optional notes for this application...",
    )

    if st.button("Save to Job Tracker"):
        try:
            job_id = save_job(package, notes=notes)
            st.success(f"Saved job #{job_id} to the local tracker.")
        except Exception as exc:
            st.error(f"Could not save job: {exc}")


def render_tracker_tab() -> None:
    """Render the local SQLite job tracker."""

    try:
        init_db()
        jobs = get_all_jobs()
    except Exception as exc:
        st.error(f"Could not load job tracker: {exc}")
        return

    st.header("Job Tracker")

    if not jobs:
        st.info("No saved jobs yet. Generate an application package, then save it to the tracker.")
        return

    status_filter = st.selectbox("Filter by status", ["All"] + ALLOWED_STATUSES)
    filtered_jobs = [
        job for job in jobs if status_filter == "All" or job["status"] == status_filter
    ]

    if not filtered_jobs:
        st.info("No jobs match this status filter.")
        return

    st.dataframe(
        filtered_jobs,
        hide_index=True,
        use_container_width=True,
        column_order=[
            "id",
            "company_name",
            "role_title",
            "location",
            "work_mode",
            "match_score",
            "match_confidence",
            "status",
            "date_added",
            "follow_up_date",
        ],
    )

    job_options = {
        f"#{job['id']} - {job.get('company_name') or 'Unknown company'} - {job.get('role_title') or 'Unknown role'}": job
        for job in filtered_jobs
    }
    selected_label = st.selectbox("Select a saved job", list(job_options.keys()))
    selected_job = job_options[selected_label]
    job_id = int(selected_job["id"])

    st.subheader("Update Selected Job")
    new_status = st.selectbox(
        "Status",
        ALLOWED_STATUSES,
        index=ALLOWED_STATUSES.index(selected_job["status"])
        if selected_job["status"] in ALLOWED_STATUSES
        else 0,
    )
    new_notes = st.text_area("Notes", value=selected_job.get("notes") or "")
    new_follow_up_date = st.text_input(
        "Follow-up date",
        value=selected_job.get("follow_up_date") or "",
        placeholder="YYYY-MM-DD",
    )

    st.write("**Recommended next action:**")
    st.write(selected_job.get("recommended_next_action") or "No recommendation saved.")

    update_col, delete_col = st.columns(2)
    with update_col:
        if st.button("Update Selected Job"):
            try:
                update_job_status(job_id, new_status)
                update_job_notes(job_id, new_notes)
                update_follow_up_date(job_id, new_follow_up_date)
                st.success("Job updated.")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not update job: {exc}")

    with delete_col:
        if st.button("Delete Selected Job"):
            try:
                delete_job(job_id)
                st.success("Job deleted.")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not delete job: {exc}")


def render_profile_memory_tab() -> None:
    """Render saved candidate profile controls."""

    try:
        init_profile_db()
        profiles = get_all_profiles()
    except Exception as exc:
        st.error(f"Could not load profile memory: {exc}")
        return

    st.header("Profile Memory")
    st.info("Saved profiles are stored locally only in data/jobs.db. You can delete them at any time.")

    with st.form("create_profile_form"):
        st.subheader("Create Profile")
        profile_name = st.text_input("Profile name")
        candidate_name = st.text_input("Candidate name")
        target_roles = st.text_input("Target roles")
        preferred_locations = st.text_input("Preferred locations")
        profile_text = st.text_area("Profile text / CV text", height=260)
        submitted = st.form_submit_button("Save Profile")

        if submitted:
            try:
                profile_id = save_profile(
                    profile_name=profile_name,
                    candidate_name=candidate_name,
                    target_roles=target_roles,
                    preferred_locations=preferred_locations,
                    profile_text=profile_text,
                )
                st.success(f"Saved profile #{profile_id}.")
                st.rerun()
            except ValueError as exc:
                st.warning(str(exc))
            except Exception as exc:
                st.error(f"Could not save profile: {exc}")

    st.subheader("Saved Profiles")
    if not profiles:
        st.info("No saved profiles yet.")
        return

    st.dataframe(
        [
            {
                "id": profile["id"],
                "profile_name": profile["profile_name"],
                "candidate_name": profile["candidate_name"],
                "target_roles": profile["target_roles"],
                "preferred_locations": profile["preferred_locations"],
                "date_updated": profile["date_updated"],
            }
            for profile in profiles
        ],
        hide_index=True,
        use_container_width=True,
    )

    profile_options = {
        f"#{profile['id']} - {profile['profile_name']}": profile for profile in profiles
    }
    selected_label = st.selectbox("Select a saved profile", list(profile_options.keys()))
    selected_profile = profile_options[selected_label]
    selected_profile_id = int(selected_profile["id"])

    with st.form("edit_profile_form"):
        st.subheader("Edit Selected Profile")
        edit_profile_name = st.text_input(
            "Profile name",
            value=selected_profile.get("profile_name") or "",
            key="edit_profile_name",
        )
        edit_candidate_name = st.text_input(
            "Candidate name",
            value=selected_profile.get("candidate_name") or "",
            key="edit_candidate_name",
        )
        edit_target_roles = st.text_input(
            "Target roles",
            value=selected_profile.get("target_roles") or "",
            key="edit_target_roles",
        )
        edit_preferred_locations = st.text_input(
            "Preferred locations",
            value=selected_profile.get("preferred_locations") or "",
            key="edit_preferred_locations",
        )
        edit_profile_text = st.text_area(
            "Profile text / CV text",
            value=selected_profile.get("profile_text") or "",
            height=260,
            key="edit_profile_text",
        )

        update_clicked = st.form_submit_button("Update Profile")
        if update_clicked:
            try:
                update_profile(
                    profile_id=selected_profile_id,
                    profile_name=edit_profile_name,
                    candidate_name=edit_candidate_name,
                    target_roles=edit_target_roles,
                    preferred_locations=edit_preferred_locations,
                    profile_text=edit_profile_text,
                )
                st.success("Profile updated.")
                st.rerun()
            except ValueError as exc:
                st.warning(str(exc))
            except Exception as exc:
                st.error(f"Could not update profile: {exc}")

    if st.button("Delete Selected Profile"):
        try:
            delete_profile(selected_profile_id)
            st.success("Profile deleted.")
            st.rerun()
        except Exception as exc:
            st.error(f"Could not delete profile: {exc}")


def load_selected_profile_into_editor(profile_id: int) -> None:
    """Load a saved profile into the editable generation text area."""

    profile = get_profile_by_id(profile_id)
    if not profile:
        st.warning("Selected profile could not be loaded.")
        return

    st.session_state["candidate_profile_input"] = profile.get("profile_text") or ""
    st.session_state["loaded_profile_id"] = profile_id


st.title("JobPilot Agent")
st.write(
    "A local AI job-search assistant that helps turn a job description and candidate profile "
    "into a complete, reviewable application package."
)
st.warning(
    "Review all generated CV and cover letter content before using it. JobPilot should not invent "
    "experience, qualifications, companies, dates, tools, metrics, or achievements."
)

generate_tab, tracker_tab, profile_tab = st.tabs(
    ["Generate Application Package", "Job Tracker", "Profile Memory"]
)

with generate_tab:
    job_description = st.text_area(
        "Job description",
        height=260,
        placeholder="Paste the full job description here...",
    )

    try:
        init_profile_db()
        saved_profiles = get_all_profiles()
    except Exception as exc:
        saved_profiles = []
        st.error(f"Could not load saved profiles: {exc}")

    profile_mode = st.radio(
        "Candidate profile source",
        ["Use saved profile", "Paste profile manually"],
        horizontal=True,
        index=0 if saved_profiles else 1,
    )

    if profile_mode == "Use saved profile":
        if saved_profiles:
            profile_options = {
                f"#{profile['id']} - {profile['profile_name']}": profile["id"]
                for profile in saved_profiles
            }
            selected_profile_label = st.selectbox(
                "Saved profile",
                list(profile_options.keys()),
            )
            selected_profile_id = int(profile_options[selected_profile_label])

            if st.button("Load Saved Profile"):
                load_selected_profile_into_editor(selected_profile_id)
        else:
            st.info(
                "No saved profiles yet. You can paste a profile manually or create one in Profile Memory."
            )

    candidate_profile = st.text_area(
        "Candidate profile / CV",
        key="candidate_profile_input",
        height=260,
        placeholder="Paste the candidate profile, CV text, or work history here...",
    )

    if st.button("Generate Application Package", type="primary"):
        try:
            with st.spinner("Generating application package..."):
                result = generate_application_package(job_description, candidate_profile)
            st.session_state["last_application_package"] = result
        except JobPilotError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Something unexpected went wrong: {exc}")

    if "last_application_package" in st.session_state:
        current_package = st.session_state["last_application_package"]
        render_package(current_package)
        render_save_to_tracker(current_package)

with tracker_tab:
    render_tracker_tab()

with profile_tab:
    render_profile_memory_tab()
