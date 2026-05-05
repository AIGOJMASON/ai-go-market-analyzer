from __future__ import annotations

from typing import Any, Dict, List

from AI_GO.api.learning_promotion import LearningPromotionError, list_learning_promotions


class RefinementIntakeError(ValueError):
    pass


def _safe_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    return []


def _shape_refinement_item(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "refinement_intake_id": f"rint_{item.get('promotion_id')}",
        "promotion_id": item.get("promotion_id"),
        "promotion_source": item.get("promotion_source"),
        "candidate_id": item.get("candidate_id"),
        "pattern_key": item.get("pattern_key"),
        "route_targets": item.get("route_targets", []),
        "score": item.get("score"),
        "source_review_ids": item.get("source_review_ids", []),
    }


def list_refinement_intake(
    *,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    if limit < 1:
        raise RefinementIntakeError("limit must be >= 1")
    if offset < 0:
        raise RefinementIntakeError("offset must be >= 0")

    try:
        promotion_index = list_learning_promotions(limit=5000, offset=0)
    except LearningPromotionError as exc:
        raise RefinementIntakeError(str(exc)) from exc

    items: List[Dict[str, Any]] = []
    for promotion in _safe_list(promotion_index.get("items")):
        if not isinstance(promotion, dict):
            continue
        if str(promotion.get("promotion_status")) != "approved":
            continue
        items.append(_shape_refinement_item(promotion))

    items.sort(
        key=lambda item: str(item.get("refinement_intake_id") or ""),
        reverse=True,
    )

    paged_items = items[offset: offset + limit]

    return {
        "artifact_type": "refinement_intake_index",
        "sealed": True,
        "count": len(paged_items),
        "total": len(items),
        "limit": limit,
        "offset": offset,
        "items": paged_items,
    }