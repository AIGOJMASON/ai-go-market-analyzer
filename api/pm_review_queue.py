from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from AI_GO.api.review_decisions import REVIEW_ROOT, ReviewDecisionError, get_review_decision_by_id


class PMReviewQueueError(ValueError):
    pass


def _safe_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def _iter_review_ids() -> List[str]:
    if not REVIEW_ROOT.exists():
        return []

    review_ids: List[str] = []
    for path in sorted(REVIEW_ROOT.glob("*.json")):
        review_ids.append(path.stem)
    return review_ids


def _shape_pm_review_item(item: Dict[str, Any]) -> Dict[str, Any]:
    context = _safe_dict(item.get("context"))
    case_panel = _safe_dict(context.get("case_panel"))
    market_panel = _safe_dict(context.get("market_panel"))

    return {
        "review_decision_id": item.get("review_decision_id"),
        "closeout_id": item.get("closeout_id"),
        "review_outcome": item.get("review_outcome"),
        "pm_followup_required": bool(item.get("pm_followup_required", False)),
        "reviewed_at": item.get("reviewed_at"),
        "route_mode": item.get("route_mode"),
        "event_theme": item.get("event_theme") or market_panel.get("event_theme"),
        "case_id": case_panel.get("case_id"),
        "case_title": case_panel.get("title"),
        "reviewer_id": item.get("reviewer_id"),
        "reviewer_role": item.get("reviewer_role"),
        "notes": item.get("notes", ""),
    }


def list_pm_review_queue(
    *,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    if limit < 1:
        raise PMReviewQueueError("limit must be >= 1")
    if offset < 0:
        raise PMReviewQueueError("offset must be >= 0")

    items: List[Dict[str, Any]] = []
    for review_id in _iter_review_ids():
        try:
            decision = get_review_decision_by_id(review_id)
        except ReviewDecisionError:
            continue
        if not isinstance(decision, dict):
            continue
        if bool(decision.get("pm_followup_required", False)) is True:
            items.append(_shape_pm_review_item(decision))

    items.sort(
        key=lambda item: str(item.get("reviewed_at") or ""),
        reverse=True,
    )

    paged_items = items[offset: offset + limit]

    return {
        "artifact_type": "pm_review_queue",
        "sealed": True,
        "count": len(paged_items),
        "total": len(items),
        "limit": limit,
        "offset": offset,
        "items": paged_items,
    }


def get_pm_review_item(review_decision_id: str) -> Dict[str, Any]:
    review_decision_id = str(review_decision_id or "").strip()
    if not review_decision_id:
        raise PMReviewQueueError("review_decision_id is required")

    try:
        item = get_review_decision_by_id(review_decision_id)
    except ReviewDecisionError as exc:
        raise PMReviewQueueError(str(exc)) from exc

    if bool(item.get("pm_followup_required", False)) is not True:
        raise PMReviewQueueError(f"review decision is not PM-eligible: {review_decision_id}")

    return _shape_pm_review_item(item)