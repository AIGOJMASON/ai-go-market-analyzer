from __future__ import annotations

QUALIFICATION_REGISTRY: dict = {
    "layer_id": "external_memory.qualification",
    "accepted_artifact_types": [
        "governed_external_signal",
        "research_packet",
        "external_refinement_packet",
    ],
    "required_fields": [
        "artifact_type",
        "source_type",
        "source_quality_weight",
        "signal_quality_weight",
        "domain_relevance_weight",
        "persistence_value_weight",
        "contamination_penalty",
        "redundancy_penalty",
        "trust_class",
        "payload",
        "target_child_cores",
        "provenance",
    ],
    "blocked_trust_classes": [
        "blocked",
        "disallowed",
        "unverifiable",
    ],
    "policy_constants": {
        "source_quality_floor": 25,
        "persist_threshold": 70,
        "hold_threshold": 50,
    },
    "allowed_decisions": [
        "persist_candidate",
        "hold",
        "reject",
    ],
    "rejection_reasons": [
        "source_quality_below_floor",
        "trust_class_blocked",
        "persistence_weight_below_threshold",
        "contamination_penalty_exceeded",
        "redundancy_penalty_exceeded",
        "invalid_input",
        "missing_required_fields",
    ],
}