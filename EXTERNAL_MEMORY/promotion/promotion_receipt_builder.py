from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Dict


PROMOTION_RECEIPT_VERSION = "v5F.3"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _receipt_id(prefix: str, payload: Dict[str, Any]) -> str:
    digest = sha256(repr(sorted(payload.items())).encode("utf-8")).hexdigest()[:12]
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}_{ts}_{digest}"


def _authority() -> Dict[str, Any]:
    return {
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
    }


def _promotion_use_limits() -> Dict[str, Any]:
    return {
        "may_feed_pattern_context": True,
        "may_feed_system_brain": True,
        "may_feed_operator_visibility": True,
        "may_feed_pm_influence_directly": False,
        "may_change_recommendation": False,
        "may_change_runtime": False,
        "may_change_state": False,
        "may_execute": False,
    }


def build_promotion_receipt(
    requester_profile: str,
    target_child_core: str,
    decision: str,
    promotion_score: float,
    record_count: int,
) -> Dict[str, Any]:
    base = {
        "requester_profile": requester_profile,
        "target_child_core": target_child_core,
        "decision": decision,
        "promotion_score": promotion_score,
        "record_count": record_count,
    }

    return {
        "artifact_type": "external_memory_promotion_receipt",
        "artifact_version": PROMOTION_RECEIPT_VERSION,
        "status": "ok",
        "receipt_id": _receipt_id("extmemprom", base),
        "created_at": _utc_now(),
        "requester_profile": requester_profile,
        "target_child_core": target_child_core,
        "decision": decision,
        "promotion_decision": decision,
        "promotion_score": promotion_score,
        "record_count": record_count,
        "authority": _authority(),
        "promotion_use_limits": _promotion_use_limits(),
        "sealed": True,
    }


def build_promotion_rejection_receipt(
    requester_profile: str,
    target_child_core: str,
    failure_reason: str,
    detail: str,
    record_count: int,
    promotion_score: float | None = None,
) -> Dict[str, Any]:
    base = {
        "requester_profile": requester_profile,
        "target_child_core": target_child_core,
        "failure_reason": failure_reason,
        "detail": detail,
        "record_count": record_count,
        "promotion_score": promotion_score,
    }

    return {
        "artifact_type": "external_memory_promotion_rejection_receipt",
        "artifact_version": PROMOTION_RECEIPT_VERSION,
        "status": "rejected",
        "receipt_id": _receipt_id("extmempromrej", base),
        "created_at": _utc_now(),
        "requester_profile": requester_profile,
        "target_child_core": target_child_core,
        "failure_reason": failure_reason,
        "detail": detail,
        "record_count": record_count,
        "promotion_score": promotion_score,
        "authority": _authority(),
        "promotion_use_limits": _promotion_use_limits(),
        "sealed": True,
    }