from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from PM_CORE.child_core_management.child_core_registry import get_active_cores, get_entry


ROOT = Path(__file__).resolve().parents[2]

ROUTING_CONFIDENCE_FLOOR = 0.60
AMBIGUITY_DELTA = 0.15


def _safe_get(metadata: Dict[str, Any], key: str, default: Any = None) -> Any:
    return metadata.get(key, default)


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _resolve_registry_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    cleaned = path_value.replace("AI_GO/", "").lstrip("/")
    return ROOT / cleaned


def _load_domain_registry(entry: Dict[str, Any]) -> Dict[str, Any]:
    registry_path_value = entry.get("domain_registry_path")
    if not registry_path_value:
        return {}
    registry_path = _resolve_registry_path(registry_path_value)
    if not registry_path.exists():
        return {}
    return _read_json(registry_path)


def _collect_text(inheritance_packet: Dict[str, Any]) -> str:
    metadata = inheritance_packet.get("metadata", {})
    research_packet = inheritance_packet.get("research_packet", {})
    parts = [
        str(research_packet.get("title", "")),
        str(research_packet.get("summary", "")),
        " ".join(research_packet.get("tags", [])) if isinstance(research_packet.get("tags"), list) else "",
        str(metadata.get("domain_focus", "")),
        str(metadata.get("preferred_core_id", "")),
    ]
    return " ".join(parts).lower()


def _score_candidate(
    inheritance_packet: Dict[str, Any],
    entry: Dict[str, Any],
    domain_registry: Dict[str, Any],
) -> Dict[str, Any]:
    metadata = inheritance_packet.get("metadata", {})
    text = _collect_text(inheritance_packet)

    declared_domain_focus = str(metadata.get("domain_focus") or "").lower().strip()
    preferred_core_id = str(metadata.get("preferred_core_id") or "").strip()
    entry_core_id = str(entry.get("core_id") or "").strip()
    entry_domain_focus = str(entry.get("domain_focus") or "").lower().strip()

    research_themes = domain_registry.get("research_themes", [])
    matched_terms: List[str] = []
    score = 0.0

    if declared_domain_focus and declared_domain_focus == entry_domain_focus:
        score += 0.55
        matched_terms.append(f"domain_focus:{declared_domain_focus}")

    if preferred_core_id and preferred_core_id == entry_core_id:
        score += 0.25
        matched_terms.append(f"preferred_core_id:{preferred_core_id}")

    for phrase in research_themes:
        normalized = str(phrase).lower().strip()
        if normalized and normalized in text:
            score += 0.10
            matched_terms.append(f"research_theme:{normalized}")

    if entry_domain_focus and entry_domain_focus in text:
        score += 0.15
        matched_terms.append(f"domain_text:{entry_domain_focus}")

    if "proposal" in text and entry_domain_focus == "contractor_proposals":
        score += 0.15
        matched_terms.append("keyword:proposal")
    if "estimate" in text and entry_domain_focus == "contractor_proposals":
        score += 0.10
        matched_terms.append("keyword:estimate")
    if "quote" in text and entry_domain_focus == "contractor_proposals":
        score += 0.10
        matched_terms.append("keyword:quote")

    if "gis" in text and entry_domain_focus == "louisville_gis":
        score += 0.15
        matched_terms.append("keyword:gis")
    if "parcel" in text and entry_domain_focus == "louisville_gis":
        score += 0.10
        matched_terms.append("keyword:parcel")
    if "zoning" in text and entry_domain_focus == "louisville_gis":
        score += 0.10
        matched_terms.append("keyword:zoning")
    if "mapping" in text and entry_domain_focus == "louisville_gis":
        score += 0.10
        matched_terms.append("keyword:mapping")

    score = min(score, 1.0)

    return {
        "core_id": entry_core_id,
        "domain_focus": entry_domain_focus,
        "score": round(score, 4),
        "matched_terms": matched_terms,
    }


def determine_domain_alignment(inheritance_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns one of:
    - routable
    - ambiguous
    - not_routable
    - inactive_target
    - forbidden_route
    """
    metadata = inheritance_packet.get("metadata", {})
    route_to_child_core = bool(_safe_get(metadata, "route_to_child_core", False))
    domain_focus = _safe_get(metadata, "domain_focus")
    preferred_core_id = _safe_get(metadata, "preferred_core_id")

    if not route_to_child_core:
        return {
            "status": "not_routable",
            "reason": "inheritance packet not marked for child-core routing",
            "domain_focus": domain_focus,
            "preferred_core_id": preferred_core_id,
            "selected_core_id": None,
            "confidence": 0.0,
            "candidate_cores": [],
            "rejected_candidates": [],
            "requires_unresolved_queue": False,
        }

    if preferred_core_id:
        preferred_entry = get_entry(preferred_core_id)
        if preferred_entry is None:
            return {
                "status": "inactive_target",
                "reason": f"preferred_core_id '{preferred_core_id}' is not registered",
                "domain_focus": domain_focus,
                "preferred_core_id": preferred_core_id,
                "selected_core_id": None,
                "confidence": 0.0,
                "candidate_cores": [],
                "rejected_candidates": [],
                "requires_unresolved_queue": True,
            }
        if preferred_entry.get("status") != "active":
            return {
                "status": "inactive_target",
                "reason": f"preferred_core_id '{preferred_core_id}' is not active",
                "domain_focus": domain_focus,
                "preferred_core_id": preferred_core_id,
                "selected_core_id": None,
                "confidence": 0.0,
                "candidate_cores": [],
                "rejected_candidates": [],
                "requires_unresolved_queue": True,
            }

    active_cores = get_active_cores()
    if not active_cores:
        return {
            "status": "not_routable",
            "reason": "no active child cores are registered",
            "domain_focus": domain_focus,
            "preferred_core_id": preferred_core_id,
            "selected_core_id": None,
            "confidence": 0.0,
            "candidate_cores": [],
            "rejected_candidates": [],
            "requires_unresolved_queue": True,
        }

    candidates: List[Dict[str, Any]] = []
    for core_id, entry in active_cores.items():
        domain_registry = _load_domain_registry(entry)
        forbidden_actions = domain_registry.get("forbidden_actions", [])
        if "direct_research_ingress" not in forbidden_actions:
            return {
                "status": "forbidden_route",
                "reason": (
                    f"candidate core '{core_id}' is missing required forbidden action "
                    "'direct_research_ingress'"
                ),
                "domain_focus": domain_focus,
                "preferred_core_id": preferred_core_id,
                "selected_core_id": None,
                "confidence": 0.0,
                "candidate_cores": [],
                "rejected_candidates": [core_id],
                "requires_unresolved_queue": True,
            }

        candidates.append(_score_candidate(inheritance_packet, entry, domain_registry))

    ranked = sorted(candidates, key=lambda item: item["score"], reverse=True)
    top = ranked[0]
    second = ranked[1] if len(ranked) > 1 else None

    if top["score"] < ROUTING_CONFIDENCE_FLOOR:
        return {
            "status": "not_routable",
            "reason": "no candidate met routing confidence floor",
            "domain_focus": domain_focus,
            "preferred_core_id": preferred_core_id,
            "selected_core_id": None,
            "confidence": top["score"],
            "candidate_cores": ranked,
            "rejected_candidates": [item["core_id"] for item in ranked],
            "requires_unresolved_queue": True,
        }

    if second and (top["score"] - second["score"]) < AMBIGUITY_DELTA:
        return {
            "status": "ambiguous",
            "reason": "top candidate margin too small to justify lawful routing",
            "domain_focus": domain_focus,
            "preferred_core_id": preferred_core_id,
            "selected_core_id": None,
            "confidence": top["score"],
            "candidate_cores": ranked,
            "rejected_candidates": [],
            "requires_unresolved_queue": True,
        }

    rejected = [item["core_id"] for item in ranked if item["core_id"] != top["core_id"]]
    return {
        "status": "routable",
        "reason": "single highest-confidence active child core selected",
        "domain_focus": domain_focus,
        "preferred_core_id": preferred_core_id,
        "selected_core_id": top["core_id"],
        "confidence": top["score"],
        "candidate_cores": ranked,
        "rejected_candidates": rejected,
        "requires_unresolved_queue": False,
    }