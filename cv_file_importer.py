"""In-memory CV/profile file import for JobPilot Agent V9."""

import io
import re
from pathlib import Path

from schemas import CVFileImportResult
from skills import JobPilotError


MAX_CV_FILE_BYTES = 5 * 1024 * 1024
MIN_EXTRACTED_CHARS = 120
PARTIAL_EXTRACTED_CHARS = 500
SUPPORTED_FILE_TYPES = {"pdf", "tex", "txt", "md"}


def _get_file_type(filename: str) -> str:
    """Return the supported file extension without the leading dot."""

    suffix = Path(filename or "").suffix.lower().lstrip(".")
    return suffix if suffix in SUPPORTED_FILE_TYPES else "unknown"


def validate_uploaded_cv_file(filename: str, file_bytes: bytes) -> None:
    """Validate uploaded CV file metadata and size before extraction."""

    if not filename or not filename.strip():
        raise JobPilotError("Please select a CV/profile file before importing.")

    file_type = _get_file_type(filename)
    if file_type == "unknown":
        raise JobPilotError("Unsupported file type. Please upload a PDF, LaTeX, TXT, or Markdown file.")

    if not file_bytes:
        raise JobPilotError("The uploaded file is empty. Please upload another file or paste the text manually.")

    if len(file_bytes) > MAX_CV_FILE_BYTES:
        raise JobPilotError(
            "File is too large. Please upload a CV file under 5 MB or paste the text manually."
        )


def _decode_text_bytes(file_bytes: bytes) -> str:
    """Decode text file bytes with safe fallbacks."""

    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return file_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    return file_bytes.decode("utf-8", errors="replace")


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract selectable text from a PDF using pypdf without OCR."""

    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise JobPilotError("Missing pypdf. Install requirements, then try importing the PDF again.") from exc

    try:
        reader = PdfReader(io.BytesIO(file_bytes))
    except Exception as exc:
        raise JobPilotError(
            "Could not read this PDF. It may be malformed or protected. Please paste the CV text manually."
        ) from exc

    if len(reader.pages) == 0:
        raise JobPilotError("This PDF has no pages. Please upload another file or paste the CV text manually.")

    page_texts: list[str] = []
    for page in reader.pages:
        try:
            page_texts.append(page.extract_text() or "")
        except Exception:
            page_texts.append("")

    return "\n\n".join(page_texts)


def extract_text_from_latex(raw_text: str) -> str:
    """Extract readable text from LaTeX source without executing or compiling it."""

    text = re.sub(r"(?<!\\)%.*", "", raw_text)
    text = re.sub(r"\\href\{[^{}]*\}\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\\(section|subsection|subsubsection|textbf|textit|emph)\*?\{([^{}]*)\}", r"\2", text)
    text = re.sub(r"\\begin\{[^{}]*\}", "\n", text)
    text = re.sub(r"\\end\{[^{}]*\}", "\n", text)
    text = re.sub(r"\\item\b", "\n- ", text)
    text = re.sub(r"\\\\", "\n", text)
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})?", " ", text)
    text = text.replace("{", " ").replace("}", " ")
    text = text.replace("~", " ")
    text = re.sub(r"[ \t]+", " ", text)
    return text


def extract_text_from_plain_text(raw_text: str) -> str:
    """Return readable text from TXT or Markdown content."""

    return raw_text


def clean_extracted_cv_text(text: str) -> str:
    """Clean extracted CV text while preserving useful resume facts."""

    if not text:
        return ""

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in normalized.splitlines()]
    lines = [line for line in lines if line]

    page_number_pattern = re.compile(r"^(page\s*)?\d+\s*(of\s*\d+)?$", re.IGNORECASE)
    filtered = [line for line in lines if not page_number_pattern.match(line)]

    counts: dict[str, int] = {}
    for line in filtered:
        counts[line.lower()] = counts.get(line.lower(), 0) + 1

    cleaned_lines = [
        line
        for line in filtered
        if not (counts.get(line.lower(), 0) > 2 and len(line) < 80)
    ]

    cleaned = "\n".join(cleaned_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def import_cv_file(filename: str, file_bytes: bytes) -> CVFileImportResult:
    """Import readable CV/profile text from a supported file entirely in memory."""

    validate_uploaded_cv_file(filename, file_bytes)
    file_type = _get_file_type(filename)
    warnings: list[str] = []

    if file_type == "pdf":
        raw_text = extract_text_from_pdf(file_bytes)
        if not raw_text.strip():
            return CVFileImportResult(
                filename=filename,
                file_type=file_type,
                extracted_text="",
                extraction_status="failed",
                warnings=[
                    "No selectable text could be extracted from this PDF. Please paste the CV text manually."
                ],
            )
    else:
        raw_text = _decode_text_bytes(file_bytes)
        if file_type == "tex":
            raw_text = extract_text_from_latex(raw_text)
        else:
            raw_text = extract_text_from_plain_text(raw_text)

    extracted_text = clean_extracted_cv_text(raw_text)

    if not extracted_text:
        return CVFileImportResult(
            filename=filename,
            file_type=file_type,
            extracted_text="",
            extraction_status="failed",
            warnings=["No readable text could be extracted. Please paste the CV text manually."],
        )

    if len(extracted_text) < MIN_EXTRACTED_CHARS:
        return CVFileImportResult(
            filename=filename,
            file_type=file_type,
            extracted_text=extracted_text,
            extraction_status="failed",
            warnings=[
                "The extracted text is too short to be reliable. Please paste more CV text manually."
            ],
        )

    status = "success"
    if len(extracted_text) < PARTIAL_EXTRACTED_CHARS:
        status = "partial"
        warnings.append("The extracted text may be incomplete. Review and edit it before normalization.")

    return CVFileImportResult(
        filename=filename,
        file_type=file_type,
        extracted_text=extracted_text,
        extraction_status=status,
        warnings=warnings,
    )
