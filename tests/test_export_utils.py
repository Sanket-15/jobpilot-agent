from export_utils import (
    application_package_to_markdown,
    application_package_to_text,
    create_safe_filename,
)
from schemas import ApplicationPackage


def test_exports_include_core_sections(demo_application_package: ApplicationPackage) -> None:
    markdown = application_package_to_markdown(demo_application_package)
    text = application_package_to_text(demo_application_package)

    for section in [
        "Job Summary",
        "Match Analysis",
        "Tailored CV Summary",
        "Tailored CV Bullet Points",
        "Cover Letter",
        "ATS / Keyword Suggestions",
        "Unsupported Claims Check",
        "Interview Questions",
        "Recommended Next Action",
    ]:
        assert section in markdown
        assert section in text


def test_safe_filename_uses_company_and_role() -> None:
    assert (
        create_safe_filename("Demo Co", "Senior Python Developer", "md")
        == "jobpilot_demo_co_senior_python_developer.md"
    )
    assert create_safe_filename(None, None, "txt") == "jobpilot_application_package.txt"
