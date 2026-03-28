from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Dict


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _receipt_id(prefix: str, payload: Dict[str, Any]) -> str:
    digest = sha256(repr(sorted(payload.items())).encode("utf-8")).hexdigest()[:12]
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}_{ts}_{digest}"


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
        "receipt_id": _receipt_id("extmemprom", base),
        "created_at": _utc_now(),
        "requester_profile": requester_profile,
        "target_child_core": target_child_core,
        "decision": decision,
        "promotion_score": promotion_score,
        "record_count": record_count,
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
        "receipt_id": _receipt_id("extmempromrej", base),
        "created_at": _utc_now(),
        "requester_profile": requester_profile,
        "target_child_core": target_child_core,
        "failure_reason": failure_reason,
        "detail": detail,
        "record_count": record_count,
        "promotion_score": promotion_score,
    }