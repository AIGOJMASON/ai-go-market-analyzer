from __future__ import annotations

from typing import Any, Dict, List


FORBIDDEN_FIELDS = {
    "internal_state",
    "internal_notes",
    "private_notes",
    "debug",
    "debug_trace",
    "traceback",
    "_internal",
    "_debug",
    "_private",
}


class ReviewIndexError(ValueError):
    pass


def _assert_no_internal_field_leakage(value: Any, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in FORBIDDEN_FIELDS or key.startswith("_"):
                raise ReviewIndexError(f"internal field leakage blocked at {path}.{key}")
            _assert_no_internal_field_leakage(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _assert_no_internal_field_leakage(nested, f"{path}[{index}]")


def _validate_review(view: Dict[str, Any]) -> None:
    if not isinstance(view, dict):
        raise ReviewIndexError("each review must be a dict")

    if view.get("artifact_type") != "operator_review_view":
        raise ReviewIndexError("invalid artifact_type in review list")

    payload = view.get("payload")
    if not isinstance(payload, dict):
        raise ReviewIndexError("review payload must be dict")

    if payload.get("sealed") is not True:
        raise ReviewIndexError("operator_review_view must be sealed")


def _matches_filter(payload: Dict[str, Any], filters: Dict[str, Any]) -> bool:
    for key, value in filters.items():
        if payload.get(key) != value:
            return False
    return True


def build_operator_review_index(
    review_views: List[Dict[str, Any]],
    filters: Dict[str, Any] | None = None,
    limit: int | None = None,
    offset: int = 0,
) -> Dict[str, Any]:

    if not isinstance(review_views, list):
        raise ReviewIndexError("review_views must be a list")

    filters = filters or {}

    validated: List[Dict[str, Any]] = []

    for i, view in enumerate(review_views):
        _assert_no_internal_field_leakage(view, f"review_views[{i}]")
        _validate_review(view)
        validated.append(view)

    filtered = [
        v for v in validated if _matches_filter(v["payload"], filters)
    ]

    total_count = len(validated)
    filtered_count = len(filtered)

    # pagination
    if limit is None:
        paginated = filtered[offset:]
    else:
        paginated = filtered[offset: offset + limit]

    results = [v["payload"] for v in paginated]

    return {
        "artifact_type": "operator_review_index",
        "payload": {
            "total_count": total_count,
            "filtered_count": filtered_count,
            "results": results,
            "limit": limit,
            "offset": offset,
            "filters": filters,
            "sealed": True,
        },
    }