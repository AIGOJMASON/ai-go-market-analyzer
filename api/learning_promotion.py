from __future__ import annotations

from typing import Any, Dict, List

from AI_GO.api.learning_arbitration import LearningArbitrationError, list_learning_decisions
from AI_GO.api.learning_override import LearningOverrideError, list_learning_overrides


class LearningPromotionError(ValueError):
    pass


def _safe_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    return []


def _promotion_from_decision(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "promotion_id": f"lprom_decision_{item.get('candidate_id')}",
        "promotion_source": "arbitration",
        "candidate_id": item.get("candidate_id"),
        "pattern_key": item.get("pattern_key"),
        "promotion_status": "approved",
        "route_targets": ["refinement"],
        "score": item.get("score"),
        "source_review_ids": item.get("source_review_ids", []),
        "decision_ref": {
            "status": item.get("status"),
            "repeat_count": item.get("repeat_count", 0),
            "confirmed_count": item.get("confirmed_count", 0),
            "review_count": item.get("review_count", 0),
            "rejected_count": item.get("rejected_count", 0),
        },
    }


def _promotion_from_override(item: Dict[str, Any]) -> Dict[str, Any]:
    source_decision = item.get("source_decision", {}) if isinstance(item.get("source_decision"), dict) else {}
    return {
        "promotion_id": f"lprom_override_{item.get('override_id')}",
        "promotion_source": "override",
        "candidate_id": item.get("candidate_id"),
        "pattern_key": source_decision.get("pattern_key"),
        "promotion_status": "approved",
        "route_targets": item.get("route_targets", ["refinement"]),
        "score": source_decision.get("score"),
        "source_review_ids": source_decision.get("source_review_ids", []),
        "override_ref": {
            "override_id": item.get("override_id"),
            "reviewer_id": item.get("reviewer_id"),
            "override_outcome": item.get("override_outcome"),
        },
    }


def list_learning_promotions(
    *,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    if limit < 1:
        raise LearningPromotionError("limit must be >= 1")
    if offset < 0:
        raise LearningPromotionError("offset must be >= 0")

    promotions: List[Dict[str, Any]] = []

    try:
        decision_index = list_learning_decisions(limit=5000, offset=0)
    except LearningArbitrationError as exc:
        raise LearningPromotionError(str(exc)) from exc

    for item in _safe_list(decision_index.get("items")):
        if not isinstance(item, dict):
            continue
        if str(item.get("status")) == "approved":
            promotions.append(_promotion_from_decision(item))

    try:
        override_index = list_learning_overrides(limit=5000, offset=0)
    except LearningOverrideError as exc:
        raise LearningPromotionError(str(exc)) from exc

    for item in _safe_list(override_index.get("items")):
        if not isinstance(item, dict):
            continue
        if str(item.get("override_outcome")) == "approved":
            promotions.append(_promotion_from_override(item))

    promotions.sort(
        key=lambda item: (
            str(item.get("promotion_source") or ""),
            str(item.get("promotion_id") or ""),
        ),
        reverse=True,
    )

    paged_items = promotions[offset: offset + limit]

    return {
        "artifact_type": "learning_promotion_index",
        "sealed": True,
        "count": len(paged_items),
        "total": len(promotions),
        "limit": limit,
        "offset": offset,
        "items": paged_items,
    }