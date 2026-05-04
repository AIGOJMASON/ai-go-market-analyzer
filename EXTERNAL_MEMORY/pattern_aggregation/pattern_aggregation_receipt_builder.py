from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_success_receipt(
    artifact_type: str,
    target_core: str,
    requester_profile: str,
    recurrence_count: int,
    pattern_strength: str,
    historical_confirmation: str,
) -> Dict[str, Any]:
    return {
        "receipt_type": "external_memory_pattern_aggregation_receipt",
        "artifact_type": artifact_type,
        "status": "success",
        "target_core": target_core,
        "requester_profile": requester_profile,
        "recurrence_count": recurrence_count,
        "pattern_strength": pattern_strength,
        "historical_confirmation": historical_confirmation,
        "observed_at": _utc_now(),
    }


def build_rejection_receipt(
    artifact_type: str,
    target_core: str,
    requester_profile: str,
    failure_reason: str,
) -> Dict[str, Any]:
    return {
        "receipt_type": "external_memory_pattern_aggregation_rejection_receipt",
        "artifact_type": artifact_type,
        "status": "failed",
        "target_core": target_core,
        "requester_profile": requester_profile,
        "failure_reason": failure_reason,
        "observed_at": _utc_now(),
    }