from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


def _ts() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_strategy_packet(
    *,
    target_core: str,
    consumer_profile: str,
    requesting_surface: str,
    continuity_scope: str,
    transformation_type: str,
    distribution_id: str,
    source_request_id: str,
    packet_payload: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "packet_type": "continuity_strategy_packet",
        "packet_id": f"CSP-{uuid4().hex[:12].upper()}",
        "target_core": target_core,
        "consumer_profile": consumer_profile,
        "requesting_surface": requesting_surface,
        "continuity_scope": continuity_scope,
        "transformation_type": transformation_type,
        "distribution_id": distribution_id,
        "source_request_id": source_request_id,
        "payload": packet_payload,
        "timestamp": _ts(),
    }


def build_consumption_receipt(
    *,
    distribution_id: str,
    requesting_surface: str,
    consumer_profile: str,
    target_core: str,
    transformation_type: str,
    packet_id: str,
    upstream_policy_version: str,
    consumption_policy_version: str,
) -> Dict[str, Any]:
    return {
        "receipt_type": "continuity_consumption_receipt",
        "consumption_receipt_id": f"CCR-{uuid4().hex[:12].upper()}",
        "distribution_id": distribution_id,
        "requesting_surface": requesting_surface,
        "consumer_profile": consumer_profile,
        "target_core": target_core,
        "transformation_type": transformation_type,
        "packet_id": packet_id,
        "upstream_policy_version": upstream_policy_version,
        "consumption_policy_version": consumption_policy_version,
        "timestamp": _ts(),
    }


def build_consumption_hold_receipt(
    *,
    distribution_id: str,
    requesting_surface: str,
    consumer_profile: str,
    target_core: str,
    transformation_type: str,
    hold_reason: str,
    release_condition: str,
    upstream_policy_version: str,
    consumption_policy_version: str,
    review_window: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "receipt_type": "continuity_consumption_hold_receipt",
        "consumption_hold_id": f"CCH-{uuid4().hex[:12].upper()}",
        "distribution_id": distribution_id,
        "requesting_surface": requesting_surface,
        "consumer_profile": consumer_profile,
        "target_core": target_core,
        "transformation_type": transformation_type,
        "hold_reason": hold_reason,
        "release_condition": release_condition,
        "review_window": review_window,
        "upstream_policy_version": upstream_policy_version,
        "consumption_policy_version": consumption_policy_version,
        "timestamp": _ts(),
    }


def build_consumption_failure_receipt(
    *,
    distribution_id: Optional[str],
    requesting_surface: Optional[str],
    consumer_profile: Optional[str],
    target_core: Optional[str],
    transformation_type: Optional[str],
    rejection_code: str,
    reason: str,
    upstream_policy_version: Optional[str],
    consumption_policy_version: str,
) -> Dict[str, Any]:
    return {
        "receipt_type": "continuity_consumption_failure_receipt",
        "consumption_failure_id": f"CCF-{uuid4().hex[:12].upper()}",
        "distribution_id": distribution_id,
        "requesting_surface": requesting_surface,
        "consumer_profile": consumer_profile,
        "target_core": target_core,
        "transformation_type": transformation_type,
        "rejection_code": rejection_code,
        "reason": reason,
        "upstream_policy_version": upstream_policy_version,
        "consumption_policy_version": consumption_policy_version,
        "timestamp": _ts(),
    }