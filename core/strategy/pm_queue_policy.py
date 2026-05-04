from AI_GO.core.strategy.pm_queue_registry import PM_QUEUE_REGISTRY


def _require_dict(value, field_name: str) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be a dict")


def _require_non_empty_string(value, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _ensure_no_forbidden_fields(payload: dict) -> None:
    forbidden = set(PM_QUEUE_REGISTRY["forbidden_internal_fields"])
    for key in payload.keys():
        if key in forbidden or key.startswith("_"):
            raise ValueError(f"forbidden internal field present: {key}")


def validate_pm_planning_record(pm_planning_record: dict) -> None:
    _require_dict(pm_planning_record, "pm_planning_record")
    _ensure_no_forbidden_fields(pm_planning_record)

    if pm_planning_record.get("artifact_type") != PM_QUEUE_REGISTRY["accepted_planning_artifact_type"]:
        raise ValueError("invalid pm planning artifact_type")

    if pm_planning_record.get("artifact_version") != PM_QUEUE_REGISTRY["accepted_planning_artifact_version"]:
        raise ValueError("invalid pm planning artifact_version")

    if pm_planning_record.get("sealed") is not True:
        raise ValueError("pm_planning_record must be sealed")

    for key in (
        "planning_id",
        "core_id",
        "planning_scope",
        "source_review_id",
        "continuity_key",
        "signal_class",
        "review_class",
        "review_priority",
        "plan_class",
        "plan_priority",
        "next_step_class",
        "planning_summary",
    ):
        _require_non_empty_string(pm_planning_record.get(key), key)

    if pm_planning_record["planning_scope"] != "pm_planning_only":
        raise ValueError("invalid planning_scope")

    required_flags = PM_QUEUE_REGISTRY["required_input_flags"]
    for field_name, expected_value in required_flags.items():
        if pm_planning_record.get(field_name) is not expected_value:
            raise ValueError(f"invalid planning input flag: {field_name}")

    supporting_counts = pm_planning_record.get("supporting_counts", {})
    _require_dict(supporting_counts, "supporting_counts")
    for key in ("continuity_count", "accepted_matches", "quarantined_matches", "analog_matches"):
        value = supporting_counts.get(key)
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"supporting_counts.{key} must be a non-negative int")


def classify_queue_lane(pm_planning_record: dict) -> str:
    plan_class = pm_planning_record["plan_class"]

    if plan_class == "hold_observe":
        return "pm_hold_queue"
    if plan_class == "prepare_review":
        return "pm_review_queue"
    if plan_class == "prepare_plan":
        return "pm_planning_queue"
    if plan_class == "prepare_escalation":
        return "pm_escalation_queue"

    raise ValueError("unsupported plan_class")


def classify_queue_status(pm_planning_record: dict) -> str:
    next_step_class = pm_planning_record["next_step_class"]

    if next_step_class == "no_action":
        return "held"
    if next_step_class in {
        "queue_for_pm_review",
        "queue_for_pm_planning",
        "queue_for_pm_escalation",
    }:
        return "queued"

    raise ValueError("unsupported next_step_class")


def classify_queue_target(pm_planning_record: dict) -> str:
    next_step_class = pm_planning_record["next_step_class"]

    if next_step_class == "no_action":
        return "observe"
    if next_step_class == "queue_for_pm_review":
        return "review"
    if next_step_class == "queue_for_pm_planning":
        return "planning"
    if next_step_class == "queue_for_pm_escalation":
        return "escalation"

    raise ValueError("unsupported next_step_class")


def classify_queue_priority(pm_planning_record: dict) -> str:
    plan_priority = pm_planning_record["plan_priority"]
    if plan_priority not in PM_QUEUE_REGISTRY["approved_queue_priority_values"]:
        raise ValueError("invalid plan_priority")
    return plan_priority


def build_queue_summary(
    pm_planning_record: dict,
    queue_lane: str,
    queue_status: str,
    queue_target: str,
    queue_priority: str,
) -> str:
    signal_class = pm_planning_record["signal_class"]
    plan_class = pm_planning_record["plan_class"]

    return (
        f"PM queue placement for {signal_class}: "
        f"lane={queue_lane}, status={queue_status}, target={queue_target}, "
        f"priority={queue_priority}, plan_class={plan_class}."
    )


def build_queue_payload(pm_planning_record: dict, queue_id: str) -> dict:
    queue_lane = classify_queue_lane(pm_planning_record)
    queue_status = classify_queue_status(pm_planning_record)
    queue_target = classify_queue_target(pm_planning_record)
    queue_priority = classify_queue_priority(pm_planning_record)

    payload = {
        "artifact_type": PM_QUEUE_REGISTRY["emitted_queue_artifact_type"],
        "artifact_version": PM_QUEUE_REGISTRY["emitted_queue_artifact_version"],
        "sealed": True,
        "queue_id": queue_id,
        "core_id": pm_planning_record["core_id"],
        "queue_scope": PM_QUEUE_REGISTRY["queue_scope"],
        "source_planning_id": pm_planning_record["planning_id"],
        "continuity_key": pm_planning_record["continuity_key"],
        "signal_class": pm_planning_record["signal_class"],
        "plan_class": pm_planning_record["plan_class"],
        "plan_priority": pm_planning_record["plan_priority"],
        "next_step_class": pm_planning_record["next_step_class"],
        "queue_lane": queue_lane,
        "queue_status": queue_status,
        "queue_target": queue_target,
        "queue_priority": queue_priority,
        "queue_summary": build_queue_summary(
            pm_planning_record=pm_planning_record,
            queue_lane=queue_lane,
            queue_status=queue_status,
            queue_target=queue_target,
            queue_priority=queue_priority,
        ),
        "supporting_counts": dict(pm_planning_record["supporting_counts"]),
        "memory_only": True,
        "runtime_mutation_allowed": False,
        "execution_influence": False,
        "recommendation_mutation_allowed": False,
    }
    return payload


def validate_output_queue(pm_queue_record: dict) -> None:
    _require_dict(pm_queue_record, "pm_queue_record")
    _ensure_no_forbidden_fields(pm_queue_record)

    if pm_queue_record.get("artifact_type") != PM_QUEUE_REGISTRY["emitted_queue_artifact_type"]:
        raise ValueError("invalid pm queue artifact_type")

    if pm_queue_record.get("artifact_version") != PM_QUEUE_REGISTRY["emitted_queue_artifact_version"]:
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

    if pm_queue_record["queue_scope"] != PM_QUEUE_REGISTRY["queue_scope"]:
        raise ValueError("invalid queue_scope")

    if pm_queue_record["queue_lane"] not in PM_QUEUE_REGISTRY["approved_queue_lanes"]:
        raise ValueError("invalid queue_lane")

    if pm_queue_record["queue_status"] not in PM_QUEUE_REGISTRY["approved_queue_status_values"]:
        raise ValueError("invalid queue_status")

    if pm_queue_record["queue_target"] not in PM_QUEUE_REGISTRY["approved_queue_target_values"]:
        raise ValueError("invalid queue_target")

    if pm_queue_record["queue_priority"] not in PM_QUEUE_REGISTRY["approved_queue_priority_values"]:
        raise ValueError("invalid queue_priority")

    required_flags = PM_QUEUE_REGISTRY["required_output_flags"]
    for field_name, expected_value in required_flags.items():
        if pm_queue_record.get(field_name) is not expected_value:
            raise ValueError(f"invalid output flag: {field_name}")

    supporting_counts = pm_queue_record.get("supporting_counts", {})
    _require_dict(supporting_counts, "supporting_counts")
    for key in ("continuity_count", "accepted_matches", "quarantined_matches", "analog_matches"):
        value = supporting_counts.get(key)
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"supporting_counts.{key} must be a non-negative int")