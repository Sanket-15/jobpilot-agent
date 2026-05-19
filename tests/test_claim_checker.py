from claim_checker import check_for_unverified_claims


def test_claim_checker_allows_learning_gap_language() -> None:
    profile = "Python, SQL, Docker, Airflow, and ETL pipeline experience in data projects."
    generated = "My Docker, Airflow, and ETL background provides a foundation for moving into MLOps practices."

    result = check_for_unverified_claims(profile, generated)

    assert result.overall_integrity_status == "needs_review"
    assert result.unsupported_claims == []


def test_claim_checker_flags_unsupported_direct_experience_claim() -> None:
    profile = "Python and SQL data analysis experience."
    generated = "I developed FastAPI services and deployed LangChain systems in production."

    result = check_for_unverified_claims(profile, generated)

    assert result.overall_integrity_status == "high_risk"
    assert any("fastapi" in claim.lower() for claim in result.unsupported_claims)
    assert any("langchain" in claim.lower() for claim in result.unsupported_claims)


def test_claim_checker_allows_translated_equivalents() -> None:
    profile = "Arbeitserfahrung: Softwareentwickler mit Datenanalyse und Komponententests."
    generated = "I worked as a Software Developer with Data Analysis and component testing experience."

    result = check_for_unverified_claims(profile, generated)

    assert result.unsupported_claims == []
