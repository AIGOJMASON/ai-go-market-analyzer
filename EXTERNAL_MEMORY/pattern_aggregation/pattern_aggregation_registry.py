# AI_GO/EXTERNAL_MEMORY/pattern_aggregation/pattern_aggregation_registry.py

from __future__ import annotations

REGISTRY = {
    "accepted_artifact_type": "external_memory_promotion_artifact",
    "accepted_receipt_type": "external_memory_promotion_receipt",
    "emitted_artifact_type": "external_memory_pattern_aggregation",
    "emitted_receipt_type": "external_memory_pattern_aggregation_receipt",
    "emitted_rejection_receipt_type": "external_memory_pattern_aggregation_rejection_receipt",
    "allowed_requester_profiles": {
        "operator_reader",
        "market_analyzer_reader",
        "pm_reader",
    },
    "allowed_target_cores": {
        "market_analyzer_v1",
    },
    "required_promotion_artifact_fields": {
        "artifact_type",
        "requester_profile",
        "target_child_core",
        "decision",
        "promotion_score",
        "record_count",
        "promoted_records",
    },
    "required_promotion_receipt_fields": {
        "artifact_type",
        "requester_profile",
        "target_child_core",
        "decision",
        "promotion_score",
        "record_count",
    },
    "required_promoted_record_fields": {
        "memory_id",
        "trust_class",
        "source_quality_weight",
        "adjusted_weight",
        "payload_summary",
        "created_at",
    },
    "required_payload_summary_fields": {
        "symbol",
        "sector",
    },
    "pattern_strengths": (
        "weak_pattern",
        "forming_pattern",
        "strong_pattern",
        "dominant_pattern",
    ),
    "pattern_postures": (
        "light_pattern_context",
        "useful_pattern_context",
        "strong_pattern_context",
    ),
    "historical_confirmations": (
        "low_confirmation",
        "moderate_confirmation",
        "high_confirmation",
    ),
    "failure_reasons": {
        "invalid_promotion_artifact_type",
        "invalid_promotion_receipt_type",
        "artifact_receipt_misalignment",
        "target_not_allowed",
        "requester_profile_not_allowed",
        "promotion_status_not_promoted",
        "empty_promoted_records",
        "missing_required_fields",
        "invalid_record_shape",
    },
}