from __future__ import annotations

from typing import Any, Dict, List, Tuple

try:
    from AI_GO.EXTERNAL_MEMORY.authority.memory_authority_guard import (
        apply_memory_authority_guard,
        evaluate_memory_authority,
    )
except ModuleNotFoundError:
    from EXTERNAL_MEMORY.authority.memory_authority_guard import (
        apply_memory_authority_guard,
        evaluate_memory_authority,
    )

from .promotion_receipt_builder import (
    build_promotion_receipt,
    build_promotion_rejection_receipt,
)
from .promotion_registry import PROMOTION_REGISTRY
from .promotion_scoring import score_retrieved_records


PROMOTION_RUNTIME_VERSION = "v5F.3"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _authority() -> Dict[str, Any]:
    return dict(PROMOTION_REGISTRY["authority"])


def _promotion_use_limits() -> Dict[str, Any]:
    return dict(PROMOTION_REGISTRY["promotion_use_limits"])


def _receipt_type(receipt: Dict[str, Any]) -> str:
    return str(receipt.get("receipt_type") or receipt.get("artifact_type") or "").strip()


def _validate_inputs(
    artifact: Dict[str, Any],
    receipt: Dict[str, Any],
) -> Tuple[bool, str, str]:
    if not isinstance(artifact, dict) or not isinstance(receipt, dict):
        return False, "invalid_input", "artifact_and_receipt_must_be_dicts"

    if artifact.get("artifact_type") != PROMOTION_REGISTRY["accepted_artifact_type"]:
        return False, "invalid_artifact_type", "artifact_type_not_allowed"

    if _receipt_type(receipt) != PROMOTION_REGISTRY["accepted_receipt_type"]:
        return False, "invalid_receipt_type", "receipt_type_not_allowed"

    if receipt.get("status") in {"failed", "blocked", "rejected"}:
        return False, "invalid_receipt_type", "retrieval_receipt_status_not_ok"

    request_summary = _safe_dict(artifact.get("request_summary"))
    if request_summary.get("requester_profile") != receipt.get("requester_profile"):
        return False, "artifact_receipt_misalignment", "requester_profile_mismatch"

    if request_summary.get("target_child_core") != receipt.get("target_child_core"):
        return False, "artifact_receipt_misalignment", "target_child_core_mismatch"

    returned_count = _safe_int(artifact.get("returned_count"), -1)
    records = _safe_list(artifact.get("records"))
    if returned_count != len(records):
        return False, "artifact_receipt_misalignment", "returned_count_mismatch"

    receipt_returned_count = receipt.get("returned_count")
    if receipt_returned_count is not None and _safe_int(receipt_returned_count, -1) != returned_count:
        return False, "artifact_receipt_misalignment", "receipt_returned_count_mismatch"

    if returned_count < 1:
        return False, "empty_record_set", "no_records_returned"

    return True, "", ""


def _blocked_trust_present(records: List[Dict[str, Any]]) -> bool:
    blocked = set(PROMOTION_REGISTRY["blocked_trust_classes"])
    return any(str(record.get("trust_class", "")).strip().lower() in blocked for record in records)


def _decision_for_score(score: float) -> str:
    constants = PROMOTION_REGISTRY["policy_constants"]
    promote_threshold = _safe_float(constants.get("promote_threshold"), 95.0)
    hold_threshold = _safe_float(constants.get("hold_threshold"), 75.0)

    if score >= promote_threshold:
        return "promoted"
    if score >= hold_threshold:
        return "hold"
    return "reject"


def _build_promotion_artifact(
    *,
    artifact: Dict[str, Any],
    decision: str,
    promotion_score: float,
    scoring_record: Dict[str, Any],
) -> Dict[str, Any]:
    request_summary = _safe_dict(artifact.get("request_summary"))
    records = _safe_list(artifact.get("records"))

    promoted = decision == "promoted"

    return {
        "artifact_type": "external_memory_promotion_artifact",
        "artifact_version": PROMOTION_RUNTIME_VERSION,
        "status": decision,
        "promotion_decision": decision,
        "promotion_score": promotion_score,
        "scoring_record": scoring_record,
        "requester_profile": request_summary.get("requester_profile", ""),
        "target_child_core": request_summary.get("target_child_core", ""),
        "record_count": len(records),
        "records": records,
        "promoted": promoted,
        "reusable_advisory_signal": promoted,
        "promotion_use_limits": _promotion_use_limits(),
        "authority": _authority(),
        "limitations": [
            "promotion_is_not_truth",
            "promotion_is_not_execution_permission",
            "promotion_does_not_mutate_runtime",
            "promotion_does_not_mutate_state",
            "promotion_does_not_override_governance",
            "promotion_does_not_change_recommendations",
        ],
        "sealed": True,
    }


def _rejection_result(
    *,
    artifact: Dict[str, Any],
    failure_reason: str,
    detail: str,
    promotion_score: float | None = None,
) -> Dict[str, Any]:
    request_summary = _safe_dict(artifact.get("request_summary"))
    records = _safe_list(artifact.get("records"))

    requester_profile = str(
        request_summary.get("requester_profile")
        or artifact.get("requester_profile")
        or ""
    )
    target_child_core = str(
        request_summary.get("target_child_core")
        or artifact.get("target_child_core")
        or ""
    )

    rejection_artifact = {
        "artifact_type": "external_memory_promotion_artifact",
        "artifact_version": PROMOTION_RUNTIME_VERSION,
        "status": "reject",
        "promotion_decision": "reject",
        "failure_reason": failure_reason,
        "detail": detail,
        "promotion_score": promotion_score,
        "requester_profile": requester_profile,
        "target_child_core": target_child_core,
        "record_count": len(records),
        "records": [],
        "promoted": False,
        "reusable_advisory_signal": False,
        "promotion_use_limits": _promotion_use_limits(),
        "authority": _authority(),
        "sealed": True,
    }

    receipt = build_promotion_rejection_receipt(
        requester_profile=requester_profile,
        target_child_core=target_child_core,
        failure_reason=failure_reason,
        detail=detail,
        record_count=len(records),
        promotion_score=promotion_score,
    )

    guarded_artifact = apply_memory_authority_guard(rejection_artifact)
    guarded_receipt = apply_memory_authority_guard(receipt)

    return {
        "status": "rejected",
        "promotion_artifact": guarded_artifact,
        "promotion_receipt": guarded_receipt,
        "artifact": guarded_artifact,
        "receipt": guarded_receipt,
        "failure_reason": failure_reason,
        "detail": detail,
        "authority": guarded_artifact.get("authority", {}),
    }


def run_external_memory_promotion(
    artifact: Dict[str, Any],
    receipt: Dict[str, Any],
) -> Dict[str, Any]:
    source_artifact = _safe_dict(artifact)
    source_receipt = _safe_dict(receipt)

    valid, failure_reason, detail = _validate_inputs(source_artifact, source_receipt)
    if not valid:
        return _rejection_result(
            artifact=source_artifact,
            failure_reason=failure_reason,
            detail=detail,
            promotion_score=None,
        )

    records = _safe_list(source_artifact.get("records"))

    if _blocked_trust_present(records):
        return _rejection_result(
            artifact=source_artifact,
            failure_reason="blocked_trust_class_present",
            detail="retrieved_records_include_blocked_trust_class",
            promotion_score=None,
        )

    scoring_record = score_retrieved_records(records)
    promotion_score = _safe_float(scoring_record.get("promotion_score"))
    decision = _decision_for_score(promotion_score)

    promotion_artifact = _build_promotion_artifact(
        artifact=source_artifact,
        decision=decision,
        promotion_score=promotion_score,
        scoring_record=scoring_record,
    )
    guarded_artifact = apply_memory_authority_guard(promotion_artifact)
    guard_decision = evaluate_memory_authority(guarded_artifact)

    if guard_decision.get("allowed") is not True:
        return _rejection_result(
            artifact=source_artifact,
            failure_reason="authority_guard_blocked",
            detail="promotion_artifact_claimed_illegal_authority",
            promotion_score=promotion_score,
        )

    request_summary = _safe_dict(source_artifact.get("request_summary"))

    if decision == "reject":
        receipt_payload = build_promotion_rejection_receipt(
            requester_profile=str(request_summary.get("requester_profile", "")),
            target_child_core=str(request_summary.get("target_child_core", "")),
            failure_reason="promotion_score_below_threshold",
            detail="promotion_score_below_hold_threshold",
            record_count=len(records),
            promotion_score=promotion_score,
        )
        guarded_receipt = apply_memory_authority_guard(receipt_payload)

        return {
            "status": "rejected",
            "promotion_artifact": guarded_artifact,
            "promotion_receipt": guarded_receipt,
            "artifact": guarded_artifact,
            "receipt": guarded_receipt,
            "failure_reason": "promotion_score_below_threshold",
            "detail": "promotion_score_below_hold_threshold",
            "authority": guarded_artifact.get("authority", {}),
        }

    receipt_payload = build_promotion_receipt(
        requester_profile=str(request_summary.get("requester_profile", "")),
        target_child_core=str(request_summary.get("target_child_core", "")),
        decision=decision,
        promotion_score=promotion_score,
        record_count=len(records),
    )
    guarded_receipt = apply_memory_authority_guard(receipt_payload)

    return {
        "status": "ok",
        "promotion_artifact": guarded_artifact,
        "promotion_receipt": guarded_receipt,
        "artifact": guarded_artifact,
        "receipt": guarded_receipt,
        "decision": decision,
        "authority": guarded_artifact.get("authority", {}),
    }