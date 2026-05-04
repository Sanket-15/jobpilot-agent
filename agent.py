"""Main orchestration for JobPilot Agent."""

from claim_checker import check_for_unverified_claims
from schemas import ApplicationPackage
from skills import (
    call_gemini_json,
    create_cover_letter,
    create_tailored_cv_bullets,
    create_tailored_cv_summary,
    parse_json_response,
    validate_inputs,
)


def generate_application_package(job_description: str, candidate_profile: str) -> ApplicationPackage:
    """Generate a complete, reviewable application package.

    The workflow validates inputs, asks Gemini for structured JSON, parses that
    JSON into Pydantic models, then runs a local rule-based claim checker over
    the generated CV and cover letter content.
    """

    validate_inputs(job_description, candidate_profile)

    response_text = call_gemini_json(job_description, candidate_profile)
    package = parse_json_response(response_text)

    generated_content = "\n\n".join(
        [
            create_tailored_cv_summary(package),
            "\n".join(create_tailored_cv_bullets(package)),
            create_cover_letter(package),
        ]
    )
    local_claims_check = check_for_unverified_claims(
        candidate_profile=candidate_profile,
        generated_content=generated_content,
        job_description=job_description,
        hiring_company_name=package.job_info.company_name,
    )
    package.claims_check = local_claims_check

    return package
