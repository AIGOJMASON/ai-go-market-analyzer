# AI_GO/EXTERNAL_MEMORY/retrieval/retrieval_registry.py

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
    "default_ordering": "adjusted_weight_desc_created_at_desc",
    "authority": {
        "memory_is_truth": False,
        "memory_is_candidate_signal": True,
        "advisory_only": True,
        "read_only_to_authority_chain": True,
        "can_override_state_authority": False,
        "can_override_canon": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
        "can_execute": False,
        "can_mutate_runtime": False,
        "can_mutate_state": False,
        "can_mutate_operational_state": False,
        "can_mutate_child_core_state": False,
    },
    "failure_reasons": [
        "invalid_request_type",
        "missing_required_fields",
        "invalid_requester_profile",
        "invalid_target_child_core",
        "invalid_limit",
        "limit_exceeds_profile_max",
        "target_not_allowed_for_profile",
    ],
    "emitted_artifacts": [
        "external_memory_retrieval_artifact",
        "external_memory_retrieval_receipt",
        "external_memory_retrieval_failure_receipt",
    ],
}