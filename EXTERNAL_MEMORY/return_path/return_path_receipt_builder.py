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


def build_return_receipt(
    requester_profile: str,
    target_child_core: str,
    promotion_score: float,
    record_count: int,
    advisory_posture: str,
) -> Dict[str, Any]:
    base = {
        "requester_profile": requester_profile,
        "target_child_core": target_child_core,
        "promotion_score": promotion_score,
        "record_count": record_count,
        "advisory_posture": advisory_posture,
    }
    return {
        "artifact_type": "external_memory_return_receipt",
        "receipt_id": _receipt_id("extmemreturn", base),
        "created_at": _utc_now(),
        "requester_profile": requester_profile,
        "target_child_core": target_child_core,
        "promotion_score": promotion_score,
        "record_count": record_count,
        "advisory_posture": advisory_posture,
    }


def build_return_rejection_receipt(
    requester_profile: str,
    target_child_core: str,
    failure_reason: str,
    detail: str,
) -> Dict[str, Any]:
    base = {
        "requester_profile": requester_profile,
        "target_child_core": target_child_core,
        "failure_reason": failure_reason,
        "detail": detail,
    }
    return {
        "artifact_type": "external_memory_return_rejection_receipt",
        "receipt_id": _receipt_id("extmemreturnrej", base),
        "created_at": _utc_now(),
        "requester_profile": requester_profile,
        "target_child_core": target_child_core,
        "failure_reason": failure_reason,
        "detail": detail,
    }