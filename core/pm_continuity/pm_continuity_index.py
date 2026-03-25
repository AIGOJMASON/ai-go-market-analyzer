from copy import deepcopy

from AI_GO.core.pm_continuity.pm_continuity_policy import (
    build_empty_index,
    validate_existing_index,
    validate_index_entry,
    validate_output_index,
    validate_output_record,
)


def update_pm_continuity_index(
    pm_continuity_record: dict,
    index_id: str,
    existing_index: dict | None = None,
) -> dict:
    """
    Update a bounded pm_continuity_index with one sealed pm_continuity_record.

    The index groups continuity truth by continuity_key and preserves
    cumulative count plus the last seen case and record identifiers.
    """
    validate_output_record(pm_continuity_record)

    if existing_index is None:
        index_payload = build_empty_index(index_id=index_id)
    else:
        validate_existing_index(existing_index)
        index_payload = deepcopy(existing_index)
        if index_payload.get("index_id") != index_id:
            raise ValueError("index_id mismatch")

    continuity_key = pm_continuity_record["continuity_key"]
    entries = index_payload["entries"]

    matched = False
    for entry in entries:
        if entry["continuity_key"] == continuity_key:
            entry["continuity_count"] += 1
            entry["last_case_id"] = pm_continuity_record["case_id"]
            entry["last_record_id"] = pm_continuity_record["record_id"]
            matched = True
            break

    if not matched:
        new_entry = {
            "continuity_key": continuity_key,
            "core_id": pm_continuity_record["core_id"],
            "signal_class": pm_continuity_record["signal_class"],
            "arbitration_class": pm_continuity_record["arbitration_class"],
            "confidence_adjustment": pm_continuity_record["confidence_adjustment"],
            "continuity_count": 1,
            "last_case_id": pm_continuity_record["case_id"],
            "last_record_id": pm_continuity_record["record_id"],
        }
        validate_index_entry(new_entry)
        entries.append(new_entry)

    index_payload["entry_count"] = len(entries)
    validate_output_index(index_payload)
    return index_payload