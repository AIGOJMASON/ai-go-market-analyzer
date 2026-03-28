from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional


APPROVED_INFLUENCE_ACTIONS = {
    "none",
    "annotation_only",
    "confidence_reduction",
    "confidence_increase",
    "filter_reinforcement",
}

CONFIDENCE_ORDER = ["low", "medium", "high"]


def _safe_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    return []


def _safe_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def _normalize_confidence(value: Any) -> str:
    if not isinstance(value, str):
        return "medium"
    normalized = value.strip().lower()
    if normalized in CONFIDENCE_ORDER:
        return normalized
    return "medium"


def _step_confidence(base_confidence: str, direction: str) -> str:
    current = _normalize_confidence(base_confidence)
    index = CONFIDENCE_ORDER.index(current)

    if direction == "down":
        index = max(0, index - 1)
    elif direction == "up":
        index = min(len(CONFIDENCE_ORDER) - 1, index + 1)

    return CONFIDENCE_ORDER[index]


def _clean_visible_text(value: Any) -> Optional[str]:
    if not isinstance(value, str):
        return None
    text = " ".join(value.strip().split())
    if not text:
        return None
    return text


def _normalize_refinement_packet(packet: Any) -> Optional[Dict[str, Any]]:
    item = _safe_dict(packet)
    if not item:
        return None

    signal = _clean_visible_text(item.get("signal"))
    insight = _clean_visible_text(item.get("visible_insight") or item.get("insight"))
    impact = _clean_visible_text(item.get("impact"))
    confidence_adjustment = _clean_visible_text(item.get("confidence_adjustment"))
    authority = _clean_visible_text(item.get("authority")) or "refinement_influence"
    source = _clean_visible_text(item.get("source")) or "refinement"

    if not signal and not insight:
        return None

    if impact not in APPROVED_INFLUENCE_ACTIONS:
        if confidence_adjustment == "down":
            impact = "confidence_reduction"
        elif confidence_adjustment == "up":
            impact = "confidence_increase"
        else:
            impact = "annotation_only"

    if confidence_adjustment not in {"down", "up", None}:
        confidence_adjustment = None

    return {
        "signal": signal or "refinement_signal",
        "visible_insight": insight or "Refinement signal present.",
        "impact": impact,
        "confidence_adjustment": confidence_adjustment,
        "authority": authority,
        "source": source,
    }


def normalize_refinement_packets(refinement_packets: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for packet in _safe_list(refinement_packets):
        item = _normalize_refinement_packet(packet)
        if item is not None:
            normalized.append(item)
    return normalized


def _determine_influence_action(refinement_packets: List[Dict[str, Any]]) -> str:
    if not refinement_packets:
        return "none"

    impacts = {packet["impact"] for packet in refinement_packets}

    if "confidence_reduction" in impacts:
        return "confidence_reduction"
    if "confidence_increase" in impacts:
        return "confidence_increase"
    if "filter_reinforcement" in impacts:
        return "filter_reinforcement"
    if "annotation_only" in impacts:
        return "annotation_only"
    return "none"


def _derive_visible_insights(refinement_packets: List[Dict[str, Any]]) -> List[str]:
    insights: List[str] = []
    seen = set()

    for packet in refinement_packets:
        line = packet.get("visible_insight")
        if not isinstance(line, str):
            continue
        if line not in seen:
            insights.append(line)
            seen.add(line)

    return insights[:3]


def _apply_display_confidence_to_recommendations(
    recommendation_panel: Dict[str, Any],
    influence_action: str,
) -> Dict[str, Any]:
    panel = deepcopy(_safe_dict(recommendation_panel))
    recommendations = _safe_list(panel.get("recommendations"))

    adjusted: List[Dict[str, Any]] = []

    for recommendation in recommendations:
        item = deepcopy(_safe_dict(recommendation))
        base_confidence = _normalize_confidence(item.get("confidence"))

        display_confidence = base_confidence
        if influence_action == "confidence_reduction":
            display_confidence = _step_confidence(base_confidence, "down")
        elif influence_action == "confidence_increase":
            display_confidence = _step_confidence(base_confidence, "up")

        item["base_confidence"] = base_confidence
        item["display_confidence"] = display_confidence
        item["influence_applied"] = influence_action in {
            "confidence_reduction",
            "confidence_increase",
        }

        adjusted.append(item)

    panel["recommendations"] = adjusted
    panel["recommendation_count"] = len(adjusted)
    return panel


def build_pm_influence_record(
    core_id: str,
    recommendation_panel: Optional[Dict[str, Any]],
    refinement_packets: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    normalized_packets = normalize_refinement_packets(refinement_packets)
    influence_action = _determine_influence_action(normalized_packets)
    visible_insights = _derive_visible_insights(normalized_packets)

    recommendation_panel_safe = _safe_dict(recommendation_panel)
    recommendation_count = int(recommendation_panel_safe.get("recommendation_count", 0) or 0)

    visible = recommendation_count > 0 and influence_action != "none"
    influenced_recommendation_panel = _apply_display_confidence_to_recommendations(
        recommendation_panel=recommendation_panel_safe,
        influence_action=influence_action,
    )

    if influence_action == "confidence_reduction":
        summary = "Displayed confidence reduced by bounded refinement influence."
    elif influence_action == "confidence_increase":
        summary = "Displayed confidence increased by bounded refinement influence."
    elif influence_action == "filter_reinforcement":
        summary = "Existing PM caution reinforced by refinement history."
    elif influence_action == "annotation_only":
        summary = "Refinement insight attached without recommendation mutation."
    else:
        summary = "No visible refinement influence applied."

    return {
        "artifact_type": "pm_influence_record",
        "core_id": core_id,
        "visible": visible,
        "influence_action": influence_action,
        "summary": summary,
        "refinement_signal_count": len(normalized_packets),
        "visible_insights": visible_insights,
        "bounded": True,
        "recommendation_panel": influenced_recommendation_panel,
        "source_packets": [
            {
                "signal": packet["signal"],
                "impact": packet["impact"],
                "authority": packet["authority"],
                "source": packet["source"],
            }
            for packet in normalized_packets
        ],
    }