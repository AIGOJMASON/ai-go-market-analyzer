from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Dict


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def should_retry(delivery_record: Dict[str, Any]) -> bool:
    """
    Return True only when the delivery record represents a failed send.

    This helper is advisory only. It must not mutate signoff or workflow truth.
    """
    if not isinstance(delivery_record, dict):
        return False
    return str(delivery_record.get("delivery_status", delivery_record.get("status", ""))).strip() == "failed"


def build_retry_attempt(original_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a bounded retry-attempt descriptor.

    This is metadata for operator/runtime use only.
    It is not a queue, not workflow truth, and not signoff authority.
    """
    source = dict(original_payload or {})
    return {
        "retry": True,
        "retry_requested_at": _utc_now_iso(),
        "original_delivery_id": source.get("delivery_id"),
        "original_sent_at": source.get("sent_at"),
        "original_status": source.get("delivery_status", source.get("status", "")),
        "original_error": source.get("error", ""),
    }