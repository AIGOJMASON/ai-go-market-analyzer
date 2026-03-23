from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_dispatch_packet(
    pm_routing_packet: Dict[str, Any],
    destination_surface: str,
) -> Dict[str, Any]:
    """
    Compress a valid PM routing packet into a dispatch-ready artifact.

    Assumes dispatch validation has already succeeded.
    """
    dispatch_id = f"DISPATCH-{uuid4()}"

    return {
        "artifact_type": "dispatch_packet",
        "dispatch_id": dispatch_id,
        "source_decision_id": pm_routing_packet["source_decision_id"],
        "source_routing_packet_id": pm_routing_packet.get("routing_packet_id"),
        "dispatch_intent": pm_routing_packet["intent"],
        "target_core": pm_routing_packet["target"],
        "destination_surface": destination_surface,
        "upstream_refs": list(pm_routing_packet["upstream_refs"]),
        "timestamp": utc_now_iso(),
    }


def build_dispatch_failure_receipt(
    reason: str,
    pm_routing_packet: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Emit a failure receipt when dispatch readiness fails.
    """
    source_decision_id = None
    if pm_routing_packet is not None:
        source_decision_id = pm_routing_packet.get("source_decision_id")

    return {
        "artifact_type": "dispatch_failure_receipt",
        "stage": "PM_DISPATCH",
        "source_decision_id": source_decision_id,
        "reason": reason,
        "propagation_status": "terminated",
        "timestamp": utc_now_iso(),
    }