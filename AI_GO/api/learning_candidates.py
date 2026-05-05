from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List

from AI_GO.api.learning_audit import LearningAuditError, list_learning_audit_index


class LearningCandidateError(ValueError):
    pass


def _safe_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    return []


def _pattern_key_from_item(item: Dict[str, Any]) -> str:
    event_theme = str(item.get("event_theme", "unknown")).strip() or "unknown"
    review_outcome = str(item.get("review_outcome", "unknown")).strip() or "unknown"
    route_mode = str(item.get("route_mode", "unknown")).strip() or "unknown"
    return f"{event_theme}|{review_outcome}|{route_mode}"


def _build_candidate(group_key: str, grouped_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    review_ids = [str(item.get("review_decision_id")) for item in grouped_items if item.get("review_decision_id")]
    event_themes = sorted(
        {
            str(item.get("event_theme", "unknown")).strip() or "unknown"
            for item in grouped_items
        }
    )
    review_outcomes = sorted(
        {
            str(item.get("review_outcome", "unknown")).strip() or "unknown"
            for item in grouped_items
        }
    )
    route_modes = sorted(
        {
            str(item.get("route_mode", "unknown")).strip() or "unknown"
            for item in grouped_items
        }
    )

    confirmed_count = sum(
        1 for item in grouped_items
        if str(item.get("review_outcome", "")).strip().lower() in {"approve", "approved", "confirmed"}
    )
    rejected_count = sum(
        1 for item in grouped_items
        if str(item.get("review_outcome", "")).strip().lower() in {"reject", "rejected"}
    )

    return {
        "candidate_id": f"candidate_{abs(hash(group_key))}",
        "pattern_key": group_key,
        "repeat_count": len(grouped_items),
        "review_count": len(grouped_items),
        "confirmed_count": confirmed_count,
        "rejected_count": rejected_count,
        "event_themes": event_themes,
        "review_outcomes": review_outcomes,
        "route_modes": route_modes,
        "source_review_ids": review_ids,
    }


def list_learning_candidates(
    *,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    if limit < 1:
        raise LearningCandidateError("limit must be >= 1")
    if offset < 0:
        raise LearningCandidateError("offset must be >= 0")

    try:
        audit_index = list_learning_audit_index(limit=5000, offset=0)
    except LearningAuditError as exc:
        raise LearningCandidateError(str(exc)) from exc

    items = _safe_list(audit_index.get("items"))
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for item in items:
        if not isinstance(item, dict):
            continue
        grouped[_pattern_key_from_item(item)].append(item)

    candidates = [
        _build_candidate(group_key, grouped_items)
        for group_key, grouped_items in grouped.items()
    ]
    candidates.sort(
        key=lambda candidate: (
            candidate["repeat_count"],
            candidate["confirmed_count"],
            candidate["pattern_key"],
        ),
        reverse=True,
    )

    paged_items = candidates[offset: offset + limit]

    return {
        "artifact_type": "learning_candidate_index",
        "sealed": True,
        "count": len(paged_items),
        "total": len(candidates),
        "limit": limit,
        "offset": offset,
        "items": paged_items,
    }