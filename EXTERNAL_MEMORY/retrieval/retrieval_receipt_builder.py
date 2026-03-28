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


def build_retrieval_receipt(
    request: Dict[str, Any],
    matched_count: int,
    returned_count: int,
) -> Dict[str, Any]:
    base = {
        "requester_profile": request.get("requester_profile"),
        "target_child_core": request.get("target_child_core"),
        "limit": request.get("limit"),
        "matched_count": matched_count,
        "returned_count": returned_count,
    }
    return {
        "artifact_type": "external_memory_retrieval_receipt",
        "receipt_id": _receipt_id("extmemread", base),
        "created_at": _utc_now(),
        "requester_profile": request.get("requester_profile"),
        "target_child_core": request.get("target_child_core"),
        "limit": request.get("limit"),
        "matched_count": matched_count,
        "returned_count": returned_count,
    }


def build_retrieval_failure_receipt(
    request: Dict[str, Any],
    failure_reason: str,
    detail: str,
) -> Dict[str, Any]:
    base = {
        "requester_profile": request.get("requester_profile"),
        "target_child_core": request.get("target_child_core"),
        "limit": request.get("limit"),
        "failure_reason": failure_reason,
        "detail": detail,
    }
    return {
        "artifact_type": "external_memory_retrieval_failure_receipt",
        "receipt_id": _receipt_id("extmemreadfail", base),
        "created_at": _utc_now(),
        "requester_profile": request.get("requester_profile"),
        "target_child_core": request.get("target_child_core"),
        "limit": request.get("limit"),
        "failure_reason": failure_reason,
        "detail": detail,
    }