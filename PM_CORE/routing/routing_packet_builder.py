from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_routing_packet(pm_decision_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compress a valid PM decision packet into a routing-ready handoff packet.

    Assumes validation has already succeeded.
    """
    target_mode = pm_decision_packet["target_mode"]

    if target_mode == "single":
        target_set: List[str] = [pm_decision_packet["target"]]
    else:
        target_set = list(pm_decision_packet["candidate_targets"])

    packet: Dict[str, Any] = {
        "artifact_type": "pm_routing_packet",
        "source_decision_id": pm_decision_packet["decision_id"],
        "intent": pm_decision_packet["intent"],
        "target_mode": target_mode,
        "rationale_summary": pm_decision_packet["rationale_summary"],
        "upstream_refs": list(pm_decision_packet["upstream_refs"]),
        "timestamp": utc_now_iso(),
    }

    if target_mode == "single":
        packet["target"] = pm_decision_packet["target"]
    else:
        packet["candidate_targets"] = list(pm_decision_packet["candidate_targets"])
        packet["candidate_set_controls"] = dict(
            pm_decision_packet["candidate_set_controls"]
        )

    packet["target_set"] = target_set
    packet["routing_readiness"] = "ready"
    return packet


def build_failure_receipt(
    reason: str,
    pm_decision_packet: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Emit a failure receipt when routing readiness fails.
    """
    decision_id = None
    if pm_decision_packet is not None:
        decision_id = pm_decision_packet.get("decision_id")

    return {
        "artifact_type": "pm_routing_failure_receipt",
        "stage": "PM_ROUTING",
        "decision_id": decision_id,
        "reason": reason,
        "propagation_status": "terminated",
        "timestamp": utc_now_iso(),
    }