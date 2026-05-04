from __future__ import annotations

try:
    from AI_GO.core.outcome_feedback.outcome_feedback_registry import (
        OUTCOME_FEEDBACK_REGISTRY,
    )
except ImportError:
    from core.outcome_feedback.outcome_feedback_registry import (
        OUTCOME_FEEDBACK_REGISTRY,
    )


def validate_closeout_record(closeout_record: dict) -> None:
    for field in OUTCOME_FEEDBACK_REGISTRY["required_closeout_fields"]:
        if not closeout_record.get(field):
            raise ValueError(f"Missing required closeout field: {field}")

    closeout_status = str(closeout_record.get("closeout_status", "")).strip().lower()
    if closeout_status not in OUTCOME_FEEDBACK_REGISTRY["accepted_closeout_statuses"]:
        raise ValueError("Closeout status is not accepted for outcome feedback")


def validate_outcome_view(outcome_view: dict) -> None:
    for field in OUTCOME_FEEDBACK_REGISTRY["required_outcome_view_fields"]:
        value = outcome_view.get(field)
        if value is None:
            raise ValueError(f"Missing required outcome view field: {field}")


def classify_outcome(
    expected_behavior: str,
    actual_outcome: str,
    outcome_code: str | None = None,
) -> str:
    normalized_code = str(outcome_code or "").strip().lower()
    if normalized_code in OUTCOME_FEEDBACK_REGISTRY["allowed_outcome_classes"]:
        return normalized_code

    expected = str(expected_behavior or "").strip().lower()
    actual = str(actual_outcome or "").strip().lower()

    if not actual:
        return "unknown"

    if expected and expected in actual:
        return "confirmed"

    expected_tokens = [token for token in expected.split() if token]
    if not expected_tokens:
        return "unknown"

    shared = [token for token in expected_tokens if token in actual]

    if not shared:
        return "failed"

    if len(shared) == len(expected_tokens):
        return "confirmed"

    return "partial"


def determine_confidence_delta(outcome_class: str) -> str:
    normalized = str(outcome_class or "").strip().lower()

    if normalized == "confirmed":
        return "up"

    if normalized == "failed":
        return "down"

    return "neutral"