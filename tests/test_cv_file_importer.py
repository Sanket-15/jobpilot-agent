import pytest

from cv_file_importer import import_cv_file
from skills import JobPilotError


LONG_FAKE_PROFILE = (
    "Demo Candidate\nPython developer with SQL, data analysis, dashboards, ETL pipelines, "
    "and stakeholder reporting experience across several internal demo projects. "
    "This is fake portfolio test data only."
)


def test_import_txt_and_markdown_extracts_text() -> None:
    txt = import_cv_file("demo.txt", LONG_FAKE_PROFILE.encode("utf-8"))
    md = import_cv_file("demo.md", f"# Profile\n\n{LONG_FAKE_PROFILE}".encode("utf-8"))

    assert "Python developer" in txt.extracted_text
    assert txt.extraction_status in {"success", "partial"}
    assert "Demo Candidate" in md.extracted_text


def test_import_latex_preserves_readable_content() -> None:
    tex = (
        r"\section{Experience}\textbf{Data Analyst} at DemoCo\\"
        r"\item Python dashboards and SQL reporting. "
        + LONG_FAKE_PROFILE
    )

    result = import_cv_file("demo.tex", tex.encode("utf-8"))

    assert "Experience" in result.extracted_text
    assert "Data Analyst" in result.extracted_text
    assert "\\section" not in result.extracted_text


@pytest.mark.parametrize(
    ("filename", "content"),
    [
        ("demo.docx", b"not supported"),
        ("empty.txt", b""),
    ],
)
def test_import_rejects_bad_files(filename: str, content: bytes) -> None:
    with pytest.raises(JobPilotError):
        import_cv_file(filename, content)


def test_import_rejects_oversized_file() -> None:
    with pytest.raises(JobPilotError):
        import_cv_file("large.txt", b"x" * (5 * 1024 * 1024 + 1))
