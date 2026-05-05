from copy import deepcopy

from AI_GO.core.strategy.pm_queue_index_registry import PM_QUEUE_INDEX_REGISTRY


def _require_dict(value, field_name: str) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be a dict")


def _require_list(value, field_name: str) -> None:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list")


def _require_non_empty_string(value, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _ensure_no_forbidden_fields(payload: dict) -> None:
    forbidden = set(PM_QUEUE_INDEX_REGISTRY["forbidden_internal_fields"])
    for key in payload.keys():
        if key in forbidden or key.startswith("_"):
            raise ValueError(f"forbidden internal field present: {key}")


def validate_pm_queue_record(pm_queue_record: dict) -> None:
    _require_dict(pm_queue_record, "pm_queue_record")
    _ensure_no_forbidden_fields(pm_queue_record)

    if pm_queue_record.get("artifact_type") != PM_QUEUE_INDEX_REGISTRY["accepted_queue_artifact_type"]:
        raise ValueError("invalid pm queue artifact_type")

    if pm_queue_record.get("artifact_version") != PM_QUEUE_INDEX_REGISTRY["accepted_queue_artifact_version"]:
        raise ValueError("invalid pm queue artifact_version")

    if pm_queue_record.get("sealed") is not True:
        raise ValueError("pm_queue_record must be sealed")

    for key in (
        "queue_id",
        "core_id",
        "queue_scope",
        "source_planning_id",
        "continuity_key",
        "signal_class",
        "plan_class",
        "plan_priority",
        "next_step_class",
        "queue_lane",
        "queue_status",
        "queue_target",
        "queue_priority",
        "queue_summary",
    ):
        _require_non_empty_string(pm_queue_record.get(key), key)

    if pm_queue_record["queue_scope"] != "pm_queue_only":
        raise ValueError("invalid queue_scope")

    if pm_queue_record["queue_lane"] not in PM_QUEUE_INDEX_REGISTRY["approved_queue_lanes"]:
        raise ValueError("invalid queue_lane")

    if pm_queue_record["queue_status"] not in PM_QUEUE_INDEX_REGISTRY["approved_queue_status_values"]:
        raise ValueError("invalid queue_status")

    if pm_queue_record["queue_target"] not in PM_QUEUE_INDEX_REGISTRY["approved_queue_target_values"]:
        raise ValueError("invalid queue_target")

    if pm_queue_record["queue_priority"] not in PM_QUEUE_INDEX_REGISTRY["approved_queue_priority_values"]:
        raise ValueError("invalid queue_priority")

    required_flags = PM_QUEUE_INDEX_REGISTRY["required_input_flags"]
    for field_name, expected_value in required_flags.items():
        if pm_queue_record.get(field_name) is not expected_value:
            raise ValueError(f"invalid queue input flag: {field_name}")

    supporting_counts = pm_queue_record.get("supporting_counts", {})
    _require_dict(supporting_counts, "supporting_counts")
    for key in ("continuity_count", "accepted_matches", "quarantined_matches", "analog_matches"):
        value = supporting_counts.get(key)
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"supporting_counts.{key} must be a non-negative int")


def validate_filters(filters: dict | None) -> dict:
    if filters is None:
        return {}

    _require_dict(filters, "filters")

    allowed = set(PM_QUEUE_INDEX_REGISTRY["approved_filter_fields"])
    normalized = {}

    for key, value in filters.items():
        if key not in allowed:
            raise ValueError(f"invalid filter field: {key}")
        _require_non_empty_string(value, key)
        normalized[key] = value

    return normalized


def validate_limit(limit: int | None) -> int | None:
    if limit is None:
        return None
    if not isinstance(limit, int) or limit < 1:
        raise ValueError("limit must be a positive int")
    return limit


def _matches_filters(pm_queue_record: dict, filters: dict) -> bool:
    for key, value in filters.items():
        if pm_queue_record.get(key) != value:
            return False
    return True


def filter_queue_records(
    pm_queue_records: list[dict],
    filters: dict | None = None,
    limit: int | None = None,
) -> list[dict]:
    _require_list(pm_queue_records, "pm_queue_records")
    normalized_filters = validate_filters(filters)
    normalized_limit = validate_limit(limit)

    matched = []
    for record in pm_queue_records:
        validate_pm_queue_record(record)
        if _matches_filters(record, normalized_filters):
            matched.append(deepcopy(record))

    if normalized_limit is not None:
        matched = matched[:normalized_limit]

    return matched


def build_index_payload(
    pm_queue_records: list[dict],
    index_id: str,
    filters: dict | None = None,
    limit: int | None = None,
) -> dict:
    _require_non_empty_string(index_id, "index_id")
    filtered_records = filter_queue_records(
        pm_queue_records=pm_queue_records,
        filters=filters,
        limit=limit,
    )

    payload = {
        "artifact_type": PM_QUEUE_INDEX_REGISTRY["emitted_index_artifact_type"],
        "artifact_version": PM_QUEUE_INDEX_REGISTRY["emitted_index_artifact_version"],
        "sealed": True,
        "index_id": index_id,
        "index_scope": PM_QUEUE_INDEX_REGISTRY["index_scope"],
        "entry_count": len(filtered_records),
        "filters": validate_filters(filters),
        "entries": filtered_records,
        "memory_only": True,
        "runtime_mutation_allowed": False,
        "execution_influence": False,
        "recommendation_mutation_allowed": False,
    }
    return payload


def validate_output_index(pm_queue_index: dict) -> None:
    _require_dict(pm_queue_index, "pm_queue_index")
    _ensure_no_forbidden_fields(pm_queue_index)

    if pm_queue_index.get("artifact_type") != PM_QUEUE_INDEX_REGISTRY["emitted_index_artifact_type"]:
        raise ValueError("invalid pm queue index artifact_type")

    if pm_queue_index.get("artifact_version") != PM_QUEUE_INDEX_REGISTRY["emitted_index_artifact_version"]:
        raise ValueError("invalid pm queue index artifact_version")

    if pm_queue_index.get("sealed") is not True:
        raise ValueError("pm_queue_index must be sealed")

    _require_non_empty_string(pm_queue_index.get("index_id"), "index_id")
    _require_non_empty_string(pm_queue_index.get("index_scope"), "index_scope")

    if pm_queue_index["index_scope"] != PM_QUEUE_INDEX_REGISTRY["index_scope"]:
        raise ValueError("invalid index_scope")

    entry_count = pm_queue_index.get("entry_count")
    entries = pm_queue_index.get("entries", [])
    if not isinstance(entry_count, int) or entry_count < 0:
        raise ValueError("entry_count must be a non-negative int")
    _require_list(entries, "entries")
    if entry_count != len(entries):
        raise ValueError("entry_count must match entries length")

    validate_filters(pm_queue_index.get("filters", {}))

    required_flags = PM_QUEUE_INDEX_REGISTRY["required_output_flags"]
    for field_name, expected_value in required_flags.items():
        if pm_queue_index.get(field_name) is not expected_value:
            raise ValueError(f"invalid output flag: {field_name}")

    for entry in entries:
        validate_pm_queue_record(entry)