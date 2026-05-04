"""Simple rule-based claim checker for JobPilot Agent V1."""

import re

from schemas import ClaimsCheck


KNOWN_DEGREE_TERMS = [
    "bachelor",
    "master",
    "mba",
    "phd",
    "doctorate",
    "degree",
    "b.sc",
    "m.sc",
    "ba",
    "ma",
]

KNOWN_CERTIFICATION_TERMS = [
    "certified",
    "certification",
    "certificate",
    "aws certified",
    "azure certified",
    "pmp",
    "scrum master",
]

COMMON_TOOLS = [
    "python",
    "sql",
    "excel",
    "tableau",
    "power bi",
    "looker",
    "javascript",
    "typescript",
    "react",
    "node",
    "django",
    "flask",
    "fastapi",
    "rest api",
    "streamlit",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "terraform",
    "git",
    "jira",
    "salesforce",
    "hubspot",
    "figma",
    "airflow",
    "etl",
    "component testing",
    "data analysis",
    "data visualization",
    "mlops",
    "machine learning",
    "ci/cd",
    "langchain",
    "langgraph",
    "pydanticai",
    "generative ai",
    "genai",
    "llm",
    "llms",
    "monitoring",
    "deployment",
    "llm orchestration",
    "agent systems",
    "azure copilot studio",
]

JOB_TITLE_TERMS = [
    "analyst",
    "engineer",
    "developer",
    "scientist",
    "manager",
    "consultant",
    "specialist",
    "designer",
    "architect",
    "lead",
    "intern",
]

SAFE_CAPITALIZED_PHRASES = {
    "ATS",
    "CV",
    "Dear Hiring Team",
    "Hiring Team",
    "JobPilot",
    "Sincerely",
    "Thank",
}

TRANSLATION_EQUIVALENTS = {
    "arbeitserfahrung": ["work experience"],
    "ausbildung": ["education"],
    "datenanalyse": ["data analysis"],
    "datenanalyst": ["data analyst"],
    "datenanalystin": ["data analyst"],
    "datenvisualisierung": ["data visualization"],
    "etl-pipelines": ["etl pipelines", "etl pipeline", "etl"],
    "etl pipelines": ["etl pipelines", "etl pipeline", "etl"],
    "fahrzeugsensordaten": ["vehicle sensor data"],
    "flottendaten": ["fleet data"],
    "komponententests": ["component testing", "component tests"],
    "software ingenieur": ["software engineer"],
    "softwareingenieur": ["software engineer"],
    "softwareentwickler": ["software developer", "software engineer"],
    "softwareentwicklerin": ["software developer", "software engineer"],
    "zertifikate": ["certifications", "certificates"],
}

LEARNING_OR_GAP_PATTERNS = [
    r"\bactively learning\b",
    r"\blearning\b",
    r"\bmotivated to\b",
    r"\bkeen to\b",
    r"\binterested in\b",
    r"\binterest in\b",
    r"\bexpand my knowledge\b",
    r"\bdevelop experience\b",
    r"\bdeveloping experience\b",
    r"\bmoving into\b",
    r"\bfoundation for\b",
    r"\bfoundation\b",
    r"\bsolid base\b",
    r"\bbase for\b",
    r"\bprovides? a .*base\b",
    r"\bprovides? a .*foundation\b",
    r"\bcontributing to\b",
    r"\blearning gap\b",
    r"\bgap\b",
    r"\bupskilling\b",
    r"\binterview preparation\b",
    r"\bto be clarified\b",
    r"\bneeds clarification\b",
]

EXPERIENCE_CLAIM_PATTERNS = [
    r"\bi (?:have|had|bring|offer|used|built|developed|implemented|created|designed|deployed|operated|managed|led|delivered|worked|worked with|completed|graduated)\b",
    r"\b(?:developed|implemented|created|designed|built|deployed|operated|managed|led|delivered|used|worked with|completed|graduated|experience with|professional experience|hands-on experience)\b",
]


def _normalize(text: str) -> str:
    """Normalize text for simple case-insensitive comparisons."""

    return re.sub(r"\s+", " ", text.lower()).strip()


def _contains_phrase(text: str, phrase: str) -> bool:
    """Check whether text contains a phrase with flexible punctuation and spacing."""

    phrase = phrase.strip()
    if not phrase:
        return False
    pattern = r"\b" + re.escape(phrase).replace(r"\ ", r"[\s\-]+") + r"\b"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def _split_sentences(text: str) -> list[str]:
    """Split generated content into simple review units."""

    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []
    return [part.strip(" -") for part in re.split(r"(?<=[.!?])\s+|[\n;]+", cleaned) if part.strip()]


def _is_learning_or_gap_statement(sentence: str) -> bool:
    """Return True when a sentence frames a topic as learning, interest, or a gap."""

    return any(re.search(pattern, sentence, flags=re.IGNORECASE) for pattern in LEARNING_OR_GAP_PATTERNS)


def _is_candidate_experience_claim(sentence: str) -> bool:
    """Return True when a sentence appears to claim candidate experience."""

    return any(re.search(pattern, sentence, flags=re.IGNORECASE) for pattern in EXPERIENCE_CLAIM_PATTERNS)


def _phrase_supported_by_profile(candidate_profile: str, generated_phrase: str) -> bool:
    """Allow exact support plus conservative German-English equivalents."""

    if _contains_phrase(candidate_profile, generated_phrase):
        return True

    generated_normalized = _normalize(generated_phrase)
    for german_phrase, english_phrases in TRANSLATION_EQUIVALENTS.items():
        if generated_normalized == german_phrase and any(
            _contains_phrase(candidate_profile, english_phrase) for english_phrase in english_phrases
        ):
            return True
        if generated_normalized in english_phrases and _contains_phrase(candidate_profile, german_phrase):
            return True

    return False


def _find_metrics_and_numbers(text: str) -> set[str]:
    """Return metrics, counts, and years-of-experience claims found in text."""

    patterns = [
        r"\b\d+(?:[.,]\d+)?\s?%",
        r"\b\d+(?:[.,]\d+)?\+?\s+(?:years?|yrs?)\b",
        r"\b\d+(?:[.,]\d+)?\+?\s+(?:users?|customers?|projects?|models?|dashboards?|reports?|pipelines?|records?|rows?|files?)\b",
        r"\b(?:increased|reduced|improved|decreased|saved|grew|cut|optimized)\s+[^.]{0,40}?\d+(?:[.,]\d+)?\s?%",
    ]
    found: set[str] = set()
    for pattern in patterns:
        found.update(match.strip() for match in re.findall(pattern, text, flags=re.IGNORECASE))
    return found


def _find_dates(text: str) -> set[str]:
    """Return date-like claims found in text."""

    patterns = [
        r"\b(?:19|20)\d{2}\b",
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+(?:19|20)\d{2}\b",
        r"\b(?:q[1-4])\s+(?:19|20)\d{2}\b",
    ]
    found: set[str] = set()
    for pattern in patterns:
        found.update(match.strip() for match in re.findall(pattern, text, flags=re.IGNORECASE))
    return found


def _find_contextual_companies(text: str) -> set[str]:
    """Find likely company names only when phrased as candidate work claims."""

    name_token = r"[A-Z][A-Za-z0-9&+'-]*"
    patterns = [
        rf"\b(?:at|for|with)\s+({name_token}(?:\s+{name_token}){{0,3}})",
        rf"\b(?:internship|role|position)\s+(?:at|with)\s+({name_token}(?:\s+{name_token}){{0,3}})",
    ]
    companies: set[str] = set()
    tool_names = {_normalize(tool) for tool in COMMON_TOOLS}
    for sentence in _split_sentences(text):
        if not _is_candidate_experience_claim(sentence):
            continue
        for pattern in patterns:
            for match in re.findall(pattern, sentence):
                phrase = match.strip().rstrip(".,;:")
                if (
                    phrase
                    and phrase not in SAFE_CAPITALIZED_PHRASES
                    and _normalize(phrase) not in tool_names
                ):
                    companies.add(phrase)
    return companies


def _find_contextual_job_titles(text: str) -> set[str]:
    """Find likely job-title claims only in candidate-related contexts."""

    patterns = [
        r"\b(?:as an|as a|as)\s+([A-Za-z][A-Za-z\s/-]{2,60})",
        r"\b(?:worked as|served as|held the role of)\s+([A-Za-z][A-Za-z\s/-]{2,60})",
    ]
    titles: set[str] = set()
    for pattern in patterns:
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            title = re.split(r"[.,;:\n]", match.strip())[0].strip()
            title = re.split(r"\b(?:on|with|using|for|at|in|and)\b", title, flags=re.IGNORECASE)[0].strip()
            title = re.sub(r"^(?:a|an)\s+", "", title, flags=re.IGNORECASE).strip()
            title_normalized = _normalize(title)
            if any(term in title_normalized for term in JOB_TITLE_TERMS):
                titles.add(title)
    return titles


def _flag_terms(
    category: str,
    generated: str,
    profile: str,
    terms: list[str],
) -> tuple[list[str], list[str]]:
    """Flag unsupported factual term claims while allowing learning/gap wording."""

    unsupported: list[str] = []
    review_warnings: list[str] = []

    for term in terms:
        for sentence in _split_sentences(generated):
            if not _contains_phrase(sentence, term) or _phrase_supported_by_profile(profile, term):
                continue
            if _is_learning_or_gap_statement(sentence):
                review_warnings.append(f"Review learning/gap wording for unsupported {category}: {term}")
                continue
            if _is_candidate_experience_claim(sentence):
                unsupported.append(f"Unsupported experience claim: {term}")

    return unsupported, review_warnings


def _flag_generated_items(
    category: str,
    generated_items: set[str],
    candidate_profile: str,
    ignored_items: set[str] | None = None,
) -> list[str]:
    """Flag generated factual items that are not supported by the candidate profile."""

    ignored_normalized = {_normalize(item) for item in ignored_items or set()}
    warnings: list[str] = []

    for item in sorted(generated_items):
        if _normalize(item) in ignored_normalized:
            continue
        if not _phrase_supported_by_profile(candidate_profile, item):
            warnings.append(f"Check unsupported {category}: {item}")

    return warnings


def _flag_candidate_claim_items(
    category: str,
    generated_content: str,
    generated_items: set[str],
    candidate_profile: str,
    ignored_items: set[str] | None = None,
) -> list[str]:
    """Flag unsupported items only when they appear in candidate-claim sentences."""

    ignored_normalized = {_normalize(item) for item in ignored_items or set()}
    warnings: list[str] = []

    for item in sorted(generated_items):
        if _normalize(item) in ignored_normalized:
            continue
        if _phrase_supported_by_profile(candidate_profile, item):
            continue
        appears_as_claim = any(
            _contains_phrase(sentence, item)
            and _is_candidate_experience_claim(sentence)
            and not _is_learning_or_gap_statement(sentence)
            for sentence in _split_sentences(generated_content)
        )
        if appears_as_claim:
            warnings.append(f"Unsupported {category}: {item}")

    return warnings


def _dedupe_claims(claims: list[str]) -> list[str]:
    """Remove duplicate or subsumed warnings while keeping messages concise."""

    unique_claims = sorted(set(claims))
    filtered: list[str] = []

    for claim in unique_claims:
        claim_value = claim.split(": ", 1)[-1].lower()
        is_subsumed = any(
            claim_value != other.split(": ", 1)[-1].lower()
            and claim_value in other.split(": ", 1)[-1].lower()
            for other in unique_claims
        )
        if not is_subsumed:
            filtered.append(claim)

    return filtered


def check_for_unverified_claims(
    candidate_profile: str,
    generated_content: str,
    job_description: str = "",
    hiring_company_name: str | None = None,
) -> ClaimsCheck:
    """Compare generated content against the candidate profile and warn on unsupported claims."""

    unsupported_claims: list[str] = []
    warnings: list[str] = []
    ignored_companies = _find_contextual_companies(job_description)
    if hiring_company_name:
        ignored_companies.add(hiring_company_name)

    for category, terms in [
        ("degree", KNOWN_DEGREE_TERMS),
        ("certification", KNOWN_CERTIFICATION_TERMS),
        ("tool or technology", COMMON_TOOLS),
    ]:
        term_claims, term_warnings = _flag_terms(
            category,
            generated_content,
            candidate_profile,
            terms,
        )
        unsupported_claims.extend(term_claims)
        warnings.extend(term_warnings)

    unsupported_claims.extend(
        _flag_candidate_claim_items(
            "company claim",
            generated_content,
            _find_contextual_companies(generated_content),
            candidate_profile,
            ignored_companies,
        )
    )
    unsupported_claims.extend(
        _flag_candidate_claim_items(
            "job title claim",
            generated_content,
            _find_contextual_job_titles(generated_content),
            candidate_profile,
        )
    )
    unsupported_claims.extend(
        _flag_candidate_claim_items(
            "date",
            generated_content,
            _find_dates(generated_content),
            candidate_profile,
        )
    )
    unsupported_claims.extend(
        _flag_candidate_claim_items(
            "metric or number",
            generated_content,
            _find_metrics_and_numbers(generated_content),
            candidate_profile,
        )
    )

    unsupported_claims = _dedupe_claims(unsupported_claims)
    warnings = sorted(set(warnings))

    if unsupported_claims:
        status = "high_risk"
    elif warnings:
        status = "needs_review"
    else:
        status = "clean"

    if not unsupported_claims and not warnings:
        warnings.append("No obvious unsupported factual claims found. Still review before using.")

    return ClaimsCheck(
        unsupported_claims=unsupported_claims,
        warnings=warnings,
        overall_integrity_status=status,
    )
