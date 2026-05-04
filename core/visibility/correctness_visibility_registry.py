from __future__ import annotations

CORRECTNESS_VISIBILITY_REGISTRY = {
    "required_output_fields": [
        "generated_at",
        "status",
        "annotation_only",
        "visibility_only",
        "core_id",
        "correctness_summary",
        "outcome_view",
        "refinement_view",
        "pm_view",
        "history_view",
    ],
    "required_outcome_fields": [
        "outcome_class",
        "confidence_delta",
    ],
    "required_refinement_fields": [
        "refinement_posture",
        "confidence_posture",
    ],
    "required_pm_fields": [
        "pm_awareness_posture",
    ],
    "forbidden_output_fields": [
        "runtime_override",
        "pm_override",
        "execution_override",
        "raw_internal_state",
    ],
}