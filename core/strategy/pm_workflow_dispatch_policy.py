from copy import deepcopy

from AI_GO.core.strategy.pm_workflow_dispatch_registry import (
    PM_WORKFLOW_DISPATCH_REGISTRY,
)


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
    forbidden = set(PM_WORKFLOW_DISPATCH_REGISTRY["forbidden_internal_fields"])
    for key in payload.keys():
        if key in forbidden or key.startswith("_"):
            raise ValueError(f"forbidden internal field present: {key}")


def validate_pm_queue_record(pm_queue_record: dict) -> None:
    _require_dict(pm_queue_record, "pm_queue_record")
    _ensure_no_forbidden_fields(pm_queue_record)

    if pm_queue_record.get("artifact_type") != PM_WORKFLOW_DISPATCH_REGISTRY["accepted_queue_artifact_type"]:
        raise ValueError("invalid pm queue artifact_type")

    if pm_queue_record.get("artifact_version") != PM_WORKFLOW_DISPATCH_REGISTRY["accepted_queue_artifact_version"]:
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

    if pm_queue_record["queue_lane"] not in PM_WORKFLOW_DISPATCH_REGISTRY["approved_queue_lanes"]:
        raise ValueError("invalid queue_lane")

    if pm_queue_record["queue_status"] not in PM_WORKFLOW_DISPATCH_REGISTRY["approved_queue_status_values"]:
        raise ValueError("invalid queue_status")

    if pm_queue_record["queue_target"] not in PM_WORKFLOW_DISPATCH_REGISTRY["approved_queue_target_values"]:
        raise ValueError("invalid queue_target")

    if pm_queue_record["queue_priority"] not in PM_WORKFLOW_DISPATCH_REGISTRY["approved_queue_priority_values"]:
        raise ValueError("invalid queue_priority")

    required_flags = PM_WORKFLOW_DISPATCH_REGISTRY["required_input_flags"]
    for field_name, expected_value in required_flags.items():
        if pm_queue_record.get(field_name) is not expected_value:
            raise ValueError(f"invalid queue input flag: {field_name}")

    supporting_counts = pm_queue_record.get("supporting_counts", {})
    _require_dict(supporting_counts, "supporting_counts")
    for key in ("continuity_count", "accepted_matches", "quarantined_matches", "analog_matches"):
        value = supporting_counts.get(key)
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"supporting_counts.{key} must be a non-negative int")


def validate_pm_queue_index(pm_queue_index: dict) -> None:
    _require_dict(pm_queue_index, "pm_queue_index")
    _ensure_no_forbidden_fields(pm_queue_index)

    if pm_queue_index.get("artifact_type") != PM_WORKFLOW_DISPATCH_REGISTRY["accepted_index_artifact_type"]:
        raise ValueError("invalid pm queue index artifact_type")

    if pm_queue_index.get("artifact_version") != PM_WORKFLOW_DISPATCH_REGISTRY["accepted_index_artifact_version"]:
        raise ValueError("invalid pm queue index artifact_version")

    if pm_queue_index.get("sealed") is not True:
        raise ValueError("pm_queue_index must be sealed")

    _require_non_empty_string(pm_queue_index.get("index_id"), "index_id")
    _require_non_empty_string(pm_queue_index.get("index_scope"), "index_scope")

    if pm_queue_index["index_scope"] != "pm_queue_index_only":
        raise ValueError("invalid index_scope")

    entry_count = pm_queue_index.get("entry_count")
    entries = pm_queue_index.get("entries", [])
    if not isinstance(entry_count, int) or entry_count < 0:
        raise ValueError("entry_count must be a non-negative int")
    _require_list(entries, "entries")
    if entry_count != len(entries):
        raise ValueError("entry_count must match entries length")

    filters = pm_queue_index.get("filters", {})
    _require_dict(filters, "filters")

    required_flags = PM_WORKFLOW_DISPATCH_REGISTRY["required_input_flags"]
    for field_name, expected_value in required_flags.items():
        if pm_queue_index.get(field_name) is not expected_value:
            raise ValueError(f"invalid queue index input flag: {field_name}")

    for entry in entries:
        validate_pm_queue_record(entry)


def ensure_queue_membership(
    pm_queue_record: dict,
    pm_queue_index: dict,
) -> None:
    queue_id = pm_queue_record["queue_id"]
    for entry in pm_queue_index["entries"]:
        if entry["queue_id"] == queue_id:
            return
    raise ValueError("queue record is not present in queue index")


def classify_dispatch_class(pm_queue_record: dict) -> str:
    lane = pm_queue_record["queue_lane"]

    if lane == "pm_hold_queue":
        return "dispatch_hold"
    if lane == "pm_review_queue":
        return "dispatch_review"
    if lane == "pm_planning_queue":
        return "dispatch_planning"
    if lane == "pm_escalation_queue":
        return "dispatch_escalation"

    raise ValueError("unsupported queue_lane")


def classify_dispatch_target(pm_queue_record: dict) -> str:
    target = pm_queue_record["queue_target"]

    if target == "observe":
        return "pm_hold_handler"
    if target == "review":
        return "pm_review_handler"
    if target == "planning":
        return "pm_planning_handler"
    if target == "escalation":
        return "pm_escalation_handler"

    raise ValueError("unsupported queue_target")


def classify_dispatch_status(pm_queue_record: dict) -> str:
    queue_status = pm_queue_record["queue_status"]
    if queue_status not in {"held", "queued"}:
        raise ValueError("unsupported queue_status")
    return "ready"


def build_dispatch_summary(
    pm_queue_record: dict,
    dispatch_class: str,
    dispatch_target: str,
    dispatch_status: str,
) -> str:
    signal_class = pm_queue_record["signal_class"]
    queue_lane = pm_queue_record["queue_lane"]
    queue_target = pm_queue_record["queue_target"]

    return (
        f"PM workflow dispatch prepared for {signal_class}: "
        f"class={dispatch_class}, target={dispatch_target}, status={dispatch_status}, "
        f"queue_lane={queue_lane}, queue_target={queue_target}."
    )


def build_dispatch_payload(
    pm_queue_record: dict,
    pm_queue_index: dict,
    dispatch_id: str,
) -> dict:
    dispatch_class = classify_dispatch_class(pm_queue_record)
    dispatch_target = classify_dispatch_target(pm_queue_record)
    dispatch_status = classify_dispatch_status(pm_queue_record)

    payload = {
        "artifact_type": PM_WORKFLOW_DISPATCH_REGISTRY["emitted_dispatch_artifact_type"],
        "artifact_version": PM_WORKFLOW_DISPATCH_REGISTRY["emitted_dispatch_artifact_version"],
        "sealed": True,
        "dispatch_id": dispatch_id,
        "core_id": pm_queue_record["core_id"],
        "dispatch_scope": PM_WORKFLOW_DISPATCH_REGISTRY["dispatch_scope"],
        "source_queue_id": pm_queue_record["queue_id"],
        "source_index_id": pm_queue_index["index_id"],
        "continuity_key": pm_queue_record["continuity_key"],
        "signal_class": pm_queue_record["signal_class"],
        "queue_lane": pm_queue_record["queue_lane"],
        "queue_status": pm_queue_record["queue_status"],
        "queue_target": pm_queue_record["queue_target"],
        "queue_priority": pm_queue_record["queue_priority"],
        "dispatch_class": dispatch_class,
        "dispatch_target": dispatch_target,
        "dispatch_status": dispatch_status,
        "dispatch_summary": build_dispatch_summary(
            pm_queue_record=pm_queue_record,
            dispatch_class=dispatch_class,
            dispatch_target=dispatch_target,
            dispatch_status=dispatch_status,
        ),
        "supporting_counts": deepcopy(pm_queue_record["supporting_counts"]),
        "memory_only": True,
        "runtime_mutation_allowed": False,
        "execution_influence": False,
        "recommendation_mutation_allowed": False,
    }
    return payload


def validate_output_dispatch(pm_workflow_dispatch_record: dict) -> None:
    _require_dict(pm_workflow_dispatch_record, "pm_workflow_dispatch_record")
    _ensure_no_forbidden_fields(pm_workflow_dispatch_record)

    if pm_workflow_dispatch_record.get("artifact_type") != PM_WORKFLOW_DISPATCH_REGISTRY["emitted_dispatch_artifact_type"]:
        raise ValueError("invalid dispatch artifact_type")

    if pm_workflow_dispatch_record.get("artifact_version") != PM_WORKFLOW_DISPATCH_REGISTRY["emitted_dispatch_artifact_version"]:
        raise ValueError("invalid dispatch artifact_version")

    if pm_workflow_dispatch_record.get("sealed") is not True:
        raise ValueError("pm_workflow_dispatch_record must be sealed")

    for key in (
        "dispatch_id",
        "core_id",
        "dispatch_scope",
        "source_queue_id",
        "source_index_id",
        "continuity_key",
        "signal_class",
        "queue_lane",
        "queue_status",
        "queue_target",
        "queue_priority",
        "dispatch_class",
        "dispatch_target",
        "dispatch_status",
        "dispatch_summary",
    ):
        _require_non_empty_string(pm_workflow_dispatch_record.get(key), key)

    if pm_workflow_dispatch_record["dispatch_scope"] != PM_WORKFLOW_DISPATCH_REGISTRY["dispatch_scope"]:
        raise ValueError("invalid dispatch_scope")

    if pm_workflow_dispatch_record["dispatch_class"] not in PM_WORKFLOW_DISPATCH_REGISTRY["approved_dispatch_classes"]:
        raise ValueError("invalid dispatch_class")

    if pm_workflow_dispatch_record["dispatch_target"] not in PM_WORKFLOW_DISPATCH_REGISTRY["approved_dispatch_targets"]:
        raise ValueError("invalid dispatch_target")

    if pm_workflow_dispatch_record["dispatch_status"] not in PM_WORKFLOW_DISPATCH_REGISTRY["approved_dispatch_status_values"]:
        raise ValueError("invalid dispatch_status")

    required_flags = PM_WORKFLOW_DISPATCH_REGISTRY["required_output_flags"]
    for field_name, expected_value in required_flags.items():
        if pm_workflow_dispatch_record.get(field_name) is not expected_value:
            raise ValueError(f"invalid output flag: {field_name}")

    supporting_counts = pm_workflow_dispatch_record.get("supporting_counts", {})
    _require_dict(supporting_counts, "supporting_counts")
    for key in ("continuity_count", "accepted_matches", "quarantined_matches", "analog_matches"):
        value = supporting_counts.get(key)
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"supporting_counts.{key} must be a non-negative int")