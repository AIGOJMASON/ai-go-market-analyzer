from __future__ import annotations

from typing import Any, Dict

from .db_writer import commit_external_memory_record


def apply_persistence_gate(qualification_record: Dict[str, Any]) -> Dict[str, Any]:
    artifact_type = qualification_record.get("artifact_type")
    decision = qualification_record.get("decision")

    if artifact_type != "external_memory_qualification_record":
        return {
            "artifact_type": "external_memory_rejection_receipt",
            "persistence_decision": "rejected",
            "rejection_reason": "invalid_input",
            "detail": "qualification_record_artifact_type_invalid",
        }

    if decision == "persist_candidate":
        return commit_external_memory_record(qualification_record)

    if decision == "hold":
        return {
            "artifact_type": "external_memory_rejection_receipt",
            "persistence_decision": "rejected",
            "rejection_reason": "held_not_persisted_in_phase_1",
            "qualification_record_id": qualification_record.get("qualification_record_id"),
            "adjusted_weight": qualification_record.get("adjusted_weight"),
        }

    return {
        "artifact_type": "external_memory_rejection_receipt",
        "persistence_decision": "rejected",
        "rejection_reason": qualification_record.get("rejection_reason", "persistence_weight_below_threshold"),
        "qualification_record_id": qualification_record.get("qualification_record_id"),
        "adjusted_weight": qualification_record.get("adjusted_weight"),
    }