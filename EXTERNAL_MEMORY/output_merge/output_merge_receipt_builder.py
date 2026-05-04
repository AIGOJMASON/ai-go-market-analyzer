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


def build_output_merge_receipt(
    target_child_core: str,
    requester_profile: str,
    projection_targets: list[str],
) -> Dict[str, Any]:
    base = {
        "target_child_core": target_child_core,
        "requester_profile": requester_profile,
        "projection_targets": tuple(projection_targets),
    }
    return {
        "artifact_type": "external_memory_output_merge_receipt",
        "receipt_id": _receipt_id("extmemmerge", base),
        "created_at": _utc_now(),
        "target_child_core": target_child_core,
        "requester_profile": requester_profile,
        "projection_targets": projection_targets,
        "merge_status": "merged",
    }


def build_output_merge_rejection_receipt(
    failure_reason: str,
    detail: str,
) -> Dict[str, Any]:
    base = {
        "failure_reason": failure_reason,
        "detail": detail,
    }
    return {
        "artifact_type": "external_memory_output_merge_rejection_receipt",
        "receipt_id": _receipt_id("extmemmergerej", base),
        "created_at": _utc_now(),
        "failure_reason": failure_reason,
        "detail": detail,
        "merge_status": "rejected",
    }