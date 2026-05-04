# AI_GO/EXTERNAL_MEMORY/return_path/return_path_registry.py

from __future__ import annotations

REGISTRY = {
    "accepted_source_artifact_types": {
        "external_memory_promotion_artifact",
        "external_memory_pattern_aggregation",
    },
    "accepted_source_receipt_types": {
        "external_memory_promotion_artifact": "external_memory_promotion_receipt",
        "external_memory_pattern_aggregation": "external_memory_pattern_aggregation_receipt",
    },
    "emitted_artifact_type": "external_memory_return_packet",
    "emitted_receipt_type": "external_memory_return_receipt",
    "emitted_rejection_receipt_type": "external_memory_return_rejection_receipt",
    "allowed_requester_profiles": {
        "operator_reader",
        "market_analyzer_reader",
        "pm_reader",
    },
    "allowed_target_child_cores": {
        "market_analyzer_v1",
    },
    "required_common_artifact_fields": {
        "artifact_type",
        "requester_profile",
        "provenance_refs",
    },
    "required_common_receipt_fields": {
        "artifact_type",
        "requester_profile",
    },
    "required_promotion_fields": {
        "decision",
        "target_child_core",
        "record_count",
        "promoted_records",
        "promotion_score",
        "advisory_summary",
    },
    "required_pattern_aggregation_fields": {
        "aggregation_status",
        "target_core",
        "recurrence_count",
        "temporal_span_days",
        "recency_weight",
        "dominant_symbol",
        "dominant_sector",
        "pattern_strength",
        "pattern_posture",
        "historical_confirmation",
        "pattern_summary",
        "promoted_memory_ids",
    },
    "failure_reasons": {
        "invalid_return_source_artifact_type",
        "invalid_return_source_receipt_type",
        "artifact_receipt_misalignment",
        "target_not_allowed",
        "requester_profile_not_allowed",
        "source_status_not_accepted",
        "missing_required_fields",
        "invalid_source_shape",
    },
}