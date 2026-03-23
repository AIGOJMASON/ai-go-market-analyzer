from __future__ import annotations

from typing import Any, Dict, Optional


DOMAIN_TO_CORE_MAP = {
    "louisville_gis": "louisville_gis_core",
    "contractor_proposals": "contractor_proposals_core",
}


def _safe_get(metadata: Dict[str, Any], key: str, default: Any = None) -> Any:
    value = metadata.get(key, default)
    return value


def determine_domain_alignment(inheritance_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resolves whether a PM inheritance packet is suitable for child-core routing.

    This module does not activate routing by itself.
    It only returns a bounded alignment decision from PM-produced metadata.
    """
    metadata = inheritance_packet.get("metadata", {})
    domain_focus = _safe_get(metadata, "domain_focus")
    route_to_child_core = bool(_safe_get(metadata, "route_to_child_core", False))
    confidence = float(_safe_get(metadata, "domain_confidence", 0.0) or 0.0)

    if not route_to_child_core:
        return {
            "status": "not_routable",
            "reason": "inheritance packet not marked for child-core routing",
            "domain_focus": domain_focus,
            "target_core_id": None,
            "confidence": confidence,
        }

    if not domain_focus:
        return {
            "status": "not_routable",
            "reason": "missing domain_focus in inheritance metadata",
            "domain_focus": None,
            "target_core_id": None,
            "confidence": confidence,
        }

    target_core_id = DOMAIN_TO_CORE_MAP.get(domain_focus)
    if target_core_id is None:
        return {
            "status": "not_routable",
            "reason": f"no registered domain mapping for domain_focus '{domain_focus}'",
            "domain_focus": domain_focus,
            "target_core_id": None,
            "confidence": confidence,
        }

    return {
        "status": "routable",
        "reason": "domain focus resolved to active child-core candidate",
        "domain_focus": domain_focus,
        "target_core_id": target_core_id,
        "confidence": confidence,
    }