from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


def _ts() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_distribution_artifact(
    *,
    target_core: str,
    continuity_scope: str,
    requested_view: str,
    consumer_profile: str,
    records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "artifact_type": "continuity_distribution_artifact",
        "distribution_id": f"CDA-{uuid4().hex[:12].upper()}",
        "target_core": target_core,
        "continuity_scope": continuity_scope,
        "requested_view": requested_view,
        "consumer_profile": consumer_profile,
        "records": records,
        "record_count": len(records),
        "timestamp": _ts(),
    }


def build_distribution_receipt(
    *,
    request_id: str,
    target_core: str,
    requesting_surface: str,
    consumer_profile: str,
    requested_view: str,
    artifact_id: str,
    policy_version: str,
) -> Dict[str, Any]:
    return {
        "receipt_type": "continuity_distribution_receipt",
        "distribution_receipt_id": f"CDR-{uuid4().hex[:12].upper()}",
        "request_id": request_id,
        "target_core": target_core,
        "requesting_surface": requesting_surface,
        "consumer_profile": consumer_profile,
        "requested_view": requested_view,
        "artifact_id": artifact_id,
        "policy_version": policy_version,
        "timestamp": _ts(),
    }


def build_distribution_hold_receipt(
    *,
    request_id: str,
    target_core: str,
    requesting_surface: str,
    consumer_profile: str,
    hold_reason: str,
    release_condition: str,
    policy_version: str,
    review_window: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "receipt_type": "continuity_distribution_hold_receipt",
        "distribution_hold_id": f"CDH-{uuid4().hex[:12].upper()}",
        "request_id": request_id,
        "target_core": target_core,
        "requesting_surface": requesting_surface,
        "consumer_profile": consumer_profile,
        "hold_reason": hold_reason,
        "release_condition": release_condition,
        "review_window": review_window,
        "policy_version": policy_version,
        "timestamp": _ts(),
    }


def build_distribution_failure_receipt(
    *,
    request_id: Optional[str],
    target_core: Optional[str],
    requesting_surface: Optional[str],
    consumer_profile: Optional[str],
    rejection_code: str,
    reason: str,
    policy_version: Optional[str],
) -> Dict[str, Any]:
    return {
        "receipt_type": "continuity_distribution_failure_receipt",
        "distribution_failure_id": f"CDF-{uuid4().hex[:12].upper()}",
        "request_id": request_id,
        "target_core": target_core,
        "requesting_surface": requesting_surface,
        "consumer_profile": consumer_profile,
        "rejection_code": rejection_code,
        "reason": reason,
        "policy_version": policy_version,
        "timestamp": _ts(),
    }