import pytest

from ats_scanner import calculate_basic_ats_score, validate_ats_inputs
from schemas import MatchAnalysis, SkillEvidence
from skills import JobPilotError, _get_model_names, validate_inputs


def test_schema_score_bounds_are_enforced() -> None:
    evidence = SkillEvidence(skill="Python", status="strong", evidence="Listed in profile.")

    with pytest.raises(Exception):
        MatchAnalysis(
            match_score=101,
            match_confidence="high",
            strong_matches=[evidence],
            partial_matches=[],
            missing_or_weak_skills=[],
            transferable_skills=[],
            risk_areas=[],
            strongest_application_angle="Python",
        )


def test_input_validation_rejects_short_text() -> None:
    with pytest.raises(JobPilotError):
        validate_inputs("short", "also short")
    with pytest.raises(JobPilotError):
        validate_ats_inputs("short", "also short")


def test_basic_ats_score_weights_clarification_keywords() -> None:
    assert calculate_basic_ats_score(["Python"], ["FastAPI"], ["MLOps"]) == 50
    assert calculate_basic_ats_score([], [], []) == 0


def test_model_name_env_override_is_first(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_MODEL_NAME", "custom-model")

    model_names = _get_model_names()

    assert model_names[0] == "custom-model"
    assert "gemini-2.0-flash" in model_names
