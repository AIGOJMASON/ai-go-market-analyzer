from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_ingress_receipt(
    dispatch_packet: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a receipt for successful ingress handoff.
    """
    ingress_id = f"INGRESS-{uuid4()}"

    return {
        "artifact_type": "ingress_receipt",
        "ingress_id": ingress_id,
        "source_dispatch_id": dispatch_packet["dispatch_id"],
        "source_decision_id": dispatch_packet["source_decision_id"],
        "target_core": dispatch_packet["target_core"],
        "destination_surface": dispatch_packet["destination_surface"],
        "handoff_status": "accepted",
        "timestamp": utc_now_iso(),
    }


def build_ingress_failure_receipt(
    reason: str,
    dispatch_packet: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Build a receipt for failed ingress validation.
    """
    dispatch_id = None
    target_core = None

    if dispatch_packet is not None:
        dispatch_id = dispatch_packet.get("dispatch_id")
        target_core = dispatch_packet.get("target_core")

    return {
        "artifact_type": "ingress_failure_receipt",
        "stage": "CHILD_CORE_INGRESS",
        "dispatch_id": dispatch_id,
        "target_core": target_core,
        "reason": reason,
        "propagation_status": "terminated",
        "timestamp": utc_now_iso(),
    }