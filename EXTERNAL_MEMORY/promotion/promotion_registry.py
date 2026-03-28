from __future__ import annotations

PROMOTION_REGISTRY: dict = {
    "layer_id": "external_memory.promotion",
    "accepted_artifact_type": "external_memory_retrieval_artifact",
    "accepted_receipt_type": "external_memory_retrieval_receipt",
    "blocked_trust_classes": [
        "blocked",
        "disallowed",
        "unverifiable",
    ],
    "policy_constants": {
        "promote_threshold": 95.0,
        "hold_threshold": 75.0,
    },
    "allowed_decisions": [
        "promoted",
        "hold",
        "reject",
    ],
    "rejection_reasons": [
        "invalid_input",
        "invalid_artifact_type",
        "invalid_receipt_type",
        "artifact_receipt_misalignment",
        "blocked_trust_class_present",
        "promotion_score_below_threshold",
        "empty_record_set",
    ],
    "emitted_artifacts": [
        "external_memory_promotion_artifact",
        "external_memory_promotion_receipt",
        "external_memory_promotion_rejection_receipt",
    ],
}