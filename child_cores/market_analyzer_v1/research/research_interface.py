from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


ALLOWED_INHERITED_ARTIFACT_TYPES = {
    "research_packet",
    "pm_decision_packet",
    "refinement_conditioning_packet",
    "market_case_record",
    "event_propagation_record",
    "market_regime_record",
}


class ResearchInterfaceError(Exception):
    """Raised when a research-facing packet is unlawful for the child core."""


def inspect_inherited_research(packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inspect whether a packet is lawful as inherited research-derived input.

    This does not accept raw RESEARCH_CORE ingress.
    It only reports whether the packet appears compatible with the local boundary.
    """
    if not isinstance(packet, dict):
        raise ResearchInterfaceError("packet must be a dict")

    artifact_type = packet.get("artifact_type")
    dispatched_by = packet.get("dispatched_by")
    target_core = packet.get("target_core")
    has_receipt = bool(packet.get("receipt") or packet.get("seal") or packet.get("provenance"))

    allowed = (
        artifact_type in ALLOWED_INHERITED_ARTIFACT_TYPES
        and dispatched_by == "PM_CORE"
        and target_core == "market_analyzer_v1"
        and has_receipt
    )

    return {
        "core_id": "market_analyzer_v1",
        "artifact_type": "research_interface_inspection",
        "allowed": allowed,
        "artifact_type_seen": artifact_type,
        "dispatched_by": dispatched_by,
        "target_core": target_core,
        "has_receipt": has_receipt,
        "notes": [] if allowed else [
            "This child core accepts inherited PM-delivered research context only."
        ],
    }