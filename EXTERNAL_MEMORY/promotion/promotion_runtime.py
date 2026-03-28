from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .promotion_receipt_builder import (
    build_promotion_receipt,
    build_promotion_rejection_receipt,
)
from .promotion_registry import PROMOTION_REGISTRY
from .promotion_scoring import score_retrieved_records


def _validate_inputs(
    artifact: Dict[str, Any],
    receipt: Dict[str, Any],
) -> Tuple[bool, str, str]:
    if artifact.get("artifact_type") != PROMOTION_REGISTRY["accepted_artifact_type"]:
        return False, "invalid_artifact_type", "artifact_type_not_allowed"

    if receipt.get("artifact_type") != PROMOTION_REGISTRY["accepted_receipt_type"]:
        return False, "invalid_receipt_type", "receipt_type_not_allowed"

    request_summary = artifact.get("request_summary", {})
    if request_summary.get("requester_profile") != receipt.get("requester_profile"):
        return False, "artifact_receipt_misalignment", "requester_profile_mismatch"

    if request_summary.get("target_child_core") != receipt.get("target_child_core"):
        return False, "artifact_receipt_misalignment", "target_child_core_mismatch"

    returned_count = int(artifact.get("returned_count", -1))
    records = artifact.get("records", [])
    if returned_count != len(records):
        return False, "artifact_receipt_misalignment", "returned_count_mismatch"

    if returned_count < 1:
        return False, "empty_record_set", "no_records_returned"

    return True, "", ""


def _blocked_trust_present(records: List[Dict[str, Any]]) -> bool:
    blocked = set(PROMOTION_REGISTRY["blocked_trust_classes"])
    return any(str(record.get("trust_class", "")).lower() in blocked for record in records)


def _decision_for_score(score: float) -> str:
    constants = PROMOTION_REGISTRY["policy_constants"]
    if score >= constants["promote_threshold"]:
        return "promoted"
    if score >= constants["hold_threshold"]:
        return "hold"
    return "reject"


def run_external_memory_promotion(
    artifact: Dict[str, Any],
    receipt: Dict[str, Any],
) -> Dict[str, Any]:
    valid, failure_reason, detail = _validate_inputs(artifact, receipt)
    request_summary = artifact.get("request_summary", {})
    requester_profile = str(request_summary.get("requester_profile", receipt.get("requester_profile", "unknown")))
    target_child_core = str(request_summary.get("target_child_core", receipt.get("target_child_core", "unknown")))
    records = artifact.get("records", [])

    if not valid:
        rejection_receipt = build_promotion_rejection_receipt(
            requester_profile=requester_profile,
            target_child_core=target_child_core,
            failure_reason=failure_reason,
            detail=detail,
            record_count=len(records),
            promotion_score=None,
        )
        return {
            "status": "failed",
            "artifact": None,
            "receipt": rejection_receipt,
        }

    if _blocked_trust_present(records):
        rejection_receipt = build_promotion_rejection_receipt(
            requester_profile=requester_profile,
            target_child_core=target_child_core,
            failure_reason="blocked_trust_class_present",
            detail="retrieved_record_contains_blocked_trust_class",
            record_count=len(records),
            promotion_score=None,
        )
        return {
            "status": "failed",
            "artifact": None,
            "receipt": rejection_receipt,
        }

    scoring = score_retrieved_records(records)
    promotion_score = float(scoring["promotion_score"])
    decision = _decision_for_score(promotion_score)

    if decision == "reject":
        rejection_receipt = build_promotion_rejection_receipt(
            requester_profile=requester_profile,
            target_child_core=target_child_core,
            failure_reason="promotion_score_below_threshold",
            detail="retrieved_records_not_strong_enough_for_reuse",
            record_count=len(records),
            promotion_score=promotion_score,
        )
        return {
            "status": "failed",
            "artifact": None,
            "receipt": rejection_receipt,
        }

    artifact_out = {
        "artifact_type": "external_memory_promotion_artifact",
        "requester_profile": requester_profile,
        "target_child_core": target_child_core,
        "decision": decision,
        "promotion_score": promotion_score,
        "record_count": len(records),
        "coherence_flags": scoring["coherence_flags"],
        "promoted_records": records,
        "rationale": {
            "average_adjusted_weight": scoring["average_adjusted_weight"],
            "average_source_quality_weight": scoring["average_source_quality_weight"],
            "average_contamination_penalty": scoring["average_contamination_penalty"],
            "coherence_bonus": scoring["coherence_bonus"],
        },
        "advisory_summary": {
            "state": "present",
            "decision": decision,
            "promotion_score": promotion_score,
            "record_count": len(records),
            "coherence_flags": scoring["coherence_flags"],
            "target_child_core": target_child_core,
        },
    }
    success_receipt = build_promotion_receipt(
        requester_profile=requester_profile,
        target_child_core=target_child_core,
        decision=decision,
        promotion_score=promotion_score,
        record_count=len(records),
    )
    return {
        "status": "ok",
        "artifact": artifact_out,
        "receipt": success_receipt,
    }