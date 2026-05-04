from __future__ import annotations

OUTCOME_FEEDBACK_REGISTRY = {
    "accepted_closeout_statuses": [
        "accepted"
    ],
    "allowed_outcome_classes": [
        "confirmed",
        "partial",
        "failed",
        "unknown",
    ],
    "allowed_confidence_delta": [
        "up",
        "down",
        "neutral",
    ],
    "required_closeout_fields": [
        "closeout_id",
        "closeout_status",
    ],
    "required_outcome_view_fields": [
        "expected_behavior",
        "actual_outcome",
    ],
    "forbidden_output_fields": [
        "runtime_override",
        "pm_override",
        "execution_override",
    ],
}