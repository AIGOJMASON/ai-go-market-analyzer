from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional


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

APPROVED_ARCHIVE_TYPES = {
    "case_closeout_record",
    "operator_review_view",
    "operator_review_index",
}

APPROVED_FILTER_FIELDS = {
    "artifact_type",
    "case_id",
    "target_child_core",
    "closeout_state",
    "final_state",
    "intake_decision",
}


class ArchiveRetrievalError(ValueError):
    """Raised when Stage 59 archive retrieval construction fails."""


def _assert_no_internal_field_leakage(value: Any, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in FORBIDDEN_FIELDS or key.startswith("_"):
                raise ArchiveRetrievalError(f"internal field leakage blocked at {path}.{key}")
            _assert_no_internal_field_leakage(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _assert_no_internal_field_leakage(nested, f"{path}[{index}]")


def _require_dict(name: str, value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ArchiveRetrievalError(f"{name} must be a dict")
    return value


def _validate_archive_item(item: Dict[str, Any], index: int) -> Dict[str, Any]:
    item_name = f"archive_items[{index}]"
    _assert_no_internal_field_leakage(item, item_name)
    item = _require_dict(item_name, deepcopy(item))

    artifact_type = item.get("artifact_type")
    if artifact_type not in APPROVED_ARCHIVE_TYPES:
        raise ArchiveRetrievalError(
            f"{item_name}.artifact_type must be one of {sorted(APPROVED_ARCHIVE_TYPES)}"
        )

    payload = item.get("payload")
    if not isinstance(payload, dict):
        raise ArchiveRetrievalError(f"{item_name}.payload must be a dict")

    if payload.get("sealed") is not True:
        raise ArchiveRetrievalError(f"{item_name}.payload.sealed must be True")

    normalized = {
        "artifact_type": artifact_type,
        "payload": payload,
    }
    return normalized


def _normalize_filters(filters: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if filters is None:
        return {}

    if not isinstance(filters, dict):
        raise ArchiveRetrievalError("filters must be a dict when provided")

    normalized: Dict[str, Any] = {}
    for key, value in filters.items():
        if key not in APPROVED_FILTER_FIELDS:
            raise ArchiveRetrievalError(
                f"filters may only use approved fields: {sorted(APPROVED_FILTER_FIELDS)}"
            )
        if value in (None, ""):
            raise ArchiveRetrievalError(f"filters.{key} must not be empty")
        normalized[key] = value

    return normalized


def _matches_filters(item: Dict[str, Any], filters: Dict[str, Any]) -> bool:
    if not filters:
        return True

    payload = item["payload"]
    for key, value in filters.items():
        if key == "artifact_type":
            if item["artifact_type"] != value:
                return False
        else:
            if payload.get(key) != value:
                return False
    return True


def build_archive_retrieval_result(
    archive_items: List[Dict[str, Any]],
    filters: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
    offset: int = 0,
    issuing_authority: str = "RUNTIME_ARCHIVE_RETRIEVAL",
) -> Dict[str, Any]:
    """
    Stage 59 — finalized archive retrieval only.

    Consumes approved finalized archive items and emits one bounded
    archive_retrieval_result.
    """
    if not isinstance(archive_items, list):
        raise ArchiveRetrievalError("archive_items must be a list")

    if offset < 0:
        raise ArchiveRetrievalError("offset must be >= 0")

    if limit is not None:
        if not isinstance(limit, int) or limit <= 0:
            raise ArchiveRetrievalError("limit must be a positive int when provided")

    normalized_filters = _normalize_filters(filters)

    validated_items = [
        _validate_archive_item(item, index) for index, item in enumerate(archive_items)
    ]

    filtered_items = [
        item for item in validated_items if _matches_filters(item, normalized_filters)
    ]

    total_count = len(validated_items)
    filtered_count = len(filtered_items)

    if limit is None:
        paginated_items = filtered_items[offset:]
    else:
        paginated_items = filtered_items[offset: offset + limit]

    results = []
    for item in paginated_items:
        results.append(
            {
                "artifact_type": item["artifact_type"],
                "payload": deepcopy(item["payload"]),
            }
        )

    return {
        "artifact_type": "archive_retrieval_result",
        "payload": {
            "issuing_authority": issuing_authority,
            "total_count": total_count,
            "filtered_count": filtered_count,
            "returned_count": len(results),
            "results": results,
            "filters": normalized_filters,
            "limit": limit,
            "offset": offset,
            "sealed": True,
        },
    }