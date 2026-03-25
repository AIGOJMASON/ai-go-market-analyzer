from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from AI_GO.api.review_decisions import REVIEW_ROOT, ReviewDecisionError, get_review_decision_by_id


class LearningAuditError(ValueError):
    pass


def _safe_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    return []


def _iter_review_decision_ids() -> List[str]:
    if not REVIEW_ROOT.exists():
        return []

    review_ids: List[str] = []
    for path in sorted(REVIEW_ROOT.glob("*.json")):
        review_ids.append(path.stem)
    return review_ids


def _normalize_learning_audit_item(review_decision: Dict[str, Any]) -> Dict[str, Any]:
    closeout_id = str(review_decision.get("closeout_id", "")).strip() or None
    decision_id = str(review_decision.get("review_decision_id", "")).strip() or None
    review_outcome = str(review_decision.get("review_outcome", "")).strip() or "unknown"
    route_mode = str(review_decision.get("route_mode", "")).strip() or "unknown"

    context = review_decision.get("context")
    if not isinstance(context, dict):
        context = {}

    market_panel = context.get("market_panel")
    if not isinstance(market_panel, dict):
        market_panel = {}

    case_panel = context.get("case_panel")
    if not isinstance(case_panel, dict):
        case_panel = {}

    event_theme = str(
        review_decision.get("event_theme")
        or market_panel.get("event_theme")
        or "unknown"
    ).strip() or "unknown"

    return {
        "review_decision_id": decision_id,
        "closeout_id": closeout_id,
        "review_outcome": review_outcome,
        "route_mode": route_mode,
        "event_theme": event_theme,
        "case_id": case_panel.get("case_id"),
        "case_title": case_panel.get("title"),
        "reviewed_at": review_decision.get("reviewed_at"),
        "reviewer_id": review_decision.get("reviewer_id"),
        "pm_followup_required": bool(review_decision.get("pm_followup_required", False)),
        "learning_eligible": review_outcome.lower() in {"approved", "approve", "confirmed"},
    }


def list_learning_audit_index(
    *,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    if limit < 1:
        raise LearningAuditError("limit must be >= 1")
    if offset < 0:
        raise LearningAuditError("offset must be >= 0")

    review_ids = _iter_review_decision_ids()
    items: List[Dict[str, Any]] = []

    for review_id in review_ids:
        try:
            review_decision = get_review_decision_by_id(review_id)
        except ReviewDecisionError:
            continue
        if not isinstance(review_decision, dict):
            continue
        items.append(_normalize_learning_audit_item(review_decision))

    items.sort(
        key=lambda item: (
            str(item.get("reviewed_at") or ""),
            str(item.get("review_decision_id") or ""),
        ),
        reverse=True,
    )

    paged_items = items[offset: offset + limit]

    return {
        "artifact_type": "learning_audit_index",
        "sealed": True,
        "count": len(paged_items),
        "total": len(items),
        "limit": limit,
        "offset": offset,
        "items": paged_items,
    }