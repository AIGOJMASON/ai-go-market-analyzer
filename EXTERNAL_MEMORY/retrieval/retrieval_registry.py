from __future__ import annotations

RETRIEVAL_REGISTRY: dict = {
    "layer_id": "external_memory.retrieval",
    "accepted_request_type": "external_memory_retrieval_request",
    "allowed_requester_profiles": {
        "operator_reader": {
            "max_records": 25,
            "allowed_targets": "*",
        },
        "market_analyzer_reader": {
            "max_records": 15,
            "allowed_targets": ["market_analyzer_v1"],
        },
        "pm_reader": {
            "max_records": 20,
            "allowed_targets": "*",
        },
    },
    "required_fields": [
        "requester_profile",
        "target_child_core",
        "limit",
    ],
    "optional_fields": [
        "source_type",
        "trust_class",
        "min_adjusted_weight",
        "symbol",
        "sector",
    ],
    "allowed_target_child_cores": [
        "market_analyzer_v1",
    ],
    "default_ordering": "created_at_desc",
    "emitted_artifacts": [
        "external_memory_retrieval_artifact",
        "external_memory_retrieval_receipt",
        "external_memory_retrieval_failure_receipt",
    ],
}