from __future__ import annotations

from typing import Any, Dict, List, Optional

from AI_GO.api.quarantine_retrieval import list_quarantined_closeouts


class ReviewQueueError(ValueError):
    pass


def _safe_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def _safe_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    return []


def _shape_review_item(item: Dict[str, Any]) -> Dict[str, Any]:
    closeout_artifact = _safe_dict(item.get("closeout_artifact"))
    case_panel = _safe_dict(closeout_artifact.get("case_panel"))
    market_panel = _safe_dict(closeout_artifact.get("market_panel"))
    governance_panel = _safe_dict(closeout_artifact.get("governance_panel"))
    rejection_panel = _safe_dict(closeout_artifact.get("rejection_panel"))

    return {
        "closeout_id": item.get("closeout_id"),
        "route_mode": item.get("route_mode"),
        "closeout_status": item.get("closeout_status"),
        "requires_review": bool(item.get("requires_review", True)),
        "case_id": case_panel.get("case_id"),
        "case_title": case_panel.get("title"),
        "event_theme": market_panel.get("event_theme"),
        "headline": market_panel.get("headline"),
        "watcher_passed": governance_panel.get("watcher_passed"),
        "approval_required": governance_panel.get("approval_required"),
        "rejection_reason": rejection_panel.get("reason"),
    }


def list_review_queue(
    *,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    if limit < 1:
        raise ReviewQueueError("limit must be >= 1")
    if offset < 0:
        raise ReviewQueueError("offset must be >= 0")

    quarantine_index = list_quarantined_closeouts(limit=5000, offset=0)
    items = [
        _shape_review_item(item)
        for item in _safe_list(quarantine_index.get("items"))
        if isinstance(item, dict) and bool(item.get("requires_review", True)) is True
    ]

    items.sort(
        key=lambda item: str(item.get("closeout_id") or ""),
        reverse=True,
    )

    paged_items = items[offset: offset + limit]

    return {
        "artifact_type": "review_queue",
        "sealed": True,
        "count": len(paged_items),
        "total": len(items),
        "limit": limit,
        "offset": offset,
        "items": paged_items,
    }


def get_review_queue_item(closeout_id: str) -> Dict[str, Any]:
    closeout_id = str(closeout_id or "").strip()
    if not closeout_id:
        raise ReviewQueueError("closeout_id is required")

    review_queue = list_review_queue(limit=5000, offset=0)
    for item in _safe_list(review_queue.get("items")):
        if not isinstance(item, dict):
            continue
        if str(item.get("closeout_id")) == closeout_id:
            return item

    raise ReviewQueueError(f"review queue item not found: {closeout_id}")