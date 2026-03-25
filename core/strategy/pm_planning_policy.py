from AI_GO.core.strategy.pm_planning_registry import PM_PLANNING_REGISTRY


def _require_dict(value, field_name: str) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be a dict")


def _require_non_empty_string(value, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _ensure_no_forbidden_fields(payload: dict) -> None:
    forbidden = set(PM_PLANNING_REGISTRY["forbidden_internal_fields"])
    for key in payload.keys():
        if key in forbidden or key.startswith("_"):
            raise ValueError(f"forbidden internal field present: {key}")


def validate_pm_review_record(pm_review_record: dict) -> None:
    _require_dict(pm_review_record, "pm_review_record")
    _ensure_no_forbidden_fields(pm_review_record)

    if pm_review_record.get("artifact_type") != PM_PLANNING_REGISTRY["accepted_review_artifact_type"]:
        raise ValueError("invalid pm review artifact_type")

    if pm_review_record.get("artifact_version") != PM_PLANNING_REGISTRY["accepted_review_artifact_version"]:
        raise ValueError("invalid pm review artifact_version")

    if pm_review_record.get("sealed") is not True:
        raise ValueError("pm_review_record must be sealed")

    for key in (
        "review_id",
        "core_id",
        "review_scope",
        "source_strategy_id",
        "continuity_key",
        "signal_class",
        "strategy_class",
        "review_class",
        "review_priority",
        "review_summary",
    ):
        _require_non_empty_string(pm_review_record.get(key), key)

    if pm_review_record["review_scope"] != "pm_review_only":
        raise ValueError("invalid review_scope")

    required_flags = PM_PLANNING_REGISTRY["required_input_flags"]
    for field_name, expected_value in required_flags.items():
        if pm_review_record.get(field_name) is not expected_value:
            raise ValueError(f"invalid review input flag: {field_name}")

    supporting_counts = pm_review_record.get("supporting_counts", {})
    _require_dict(supporting_counts, "supporting_counts")
    for key in ("continuity_count", "accepted_matches", "quarantined_matches", "analog_matches"):
        value = supporting_counts.get(key)
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"supporting_counts.{key} must be a non-negative int")


def classify_plan_class(pm_review_record: dict) -> str:
    review_class = pm_review_record["review_class"]

    if review_class == "observe":
        return "hold_observe"
    if review_class == "review":
        return "prepare_review"
    if review_class == "plan":
        return "prepare_plan"
    if review_class == "escalate":
        return "prepare_escalation"

    raise ValueError("unsupported review_class")


def classify_next_step_class(pm_review_record: dict) -> str:
    review_class = pm_review_record["review_class"]

    if review_class == "observe":
        return "no_action"
    if review_class == "review":
        return "queue_for_pm_review"
    if review_class == "plan":
        return "queue_for_pm_planning"
    if review_class == "escalate":
        return "queue_for_pm_escalation"

    raise ValueError("unsupported review_class")


def classify_plan_priority(pm_review_record: dict) -> str:
    review_priority = pm_review_record["review_priority"]
    if review_priority not in PM_PLANNING_REGISTRY["approved_plan_priority_values"]:
        raise ValueError("invalid review_priority")
    return review_priority


def build_planning_summary(
    pm_review_record: dict,
    plan_class: str,
    next_step_class: str,
    plan_priority: str,
) -> str:
    signal_class = pm_review_record["signal_class"]
    review_class = pm_review_record["review_class"]

    if plan_class == "prepare_escalation":
        return (
            f"PM planning should prepare escalation workflow for {signal_class}. "
            f"Review class={review_class}, next_step={next_step_class}, priority={plan_priority}."
        )
    if plan_class == "prepare_plan":
        return (
            f"PM planning should prepare formal planning workflow for {signal_class}. "
            f"Review class={review_class}, next_step={next_step_class}, priority={plan_priority}."
        )
    if plan_class == "prepare_review":
        return (
            f"PM planning should prepare review workflow for {signal_class}. "
            f"Review class={review_class}, next_step={next_step_class}, priority={plan_priority}."
        )
    return (
        f"PM planning should hold and observe for {signal_class}. "
        f"Review class={review_class}, next_step={next_step_class}, priority={plan_priority}."
    )


def build_planning_payload(pm_review_record: dict, planning_id: str) -> dict:
    plan_class = classify_plan_class(pm_review_record)
    next_step_class = classify_next_step_class(pm_review_record)
    plan_priority = classify_plan_priority(pm_review_record)

    payload = {
        "artifact_type": PM_PLANNING_REGISTRY["emitted_planning_artifact_type"],
        "artifact_version": PM_PLANNING_REGISTRY["emitted_planning_artifact_version"],
        "sealed": True,
        "planning_id": planning_id,
        "core_id": pm_review_record["core_id"],
        "planning_scope": PM_PLANNING_REGISTRY["planning_scope"],
        "source_review_id": pm_review_record["review_id"],
        "continuity_key": pm_review_record["continuity_key"],
        "signal_class": pm_review_record["signal_class"],
        "review_class": pm_review_record["review_class"],
        "review_priority": pm_review_record["review_priority"],
        "plan_class": plan_class,
        "plan_priority": plan_priority,
        "next_step_class": next_step_class,
        "planning_summary": build_planning_summary(
            pm_review_record=pm_review_record,
            plan_class=plan_class,
            next_step_class=next_step_class,
            plan_priority=plan_priority,
        ),
        "supporting_counts": dict(pm_review_record["supporting_counts"]),
        "memory_only": True,
        "runtime_mutation_allowed": False,
        "execution_influence": False,
        "recommendation_mutation_allowed": False,
    }
    return payload


def validate_output_planning(pm_planning_record: dict) -> None:
    _require_dict(pm_planning_record, "pm_planning_record")
    _ensure_no_forbidden_fields(pm_planning_record)

    if pm_planning_record.get("artifact_type") != PM_PLANNING_REGISTRY["emitted_planning_artifact_type"]:
        raise ValueError("invalid pm planning artifact_type")

    if pm_planning_record.get("artifact_version") != PM_PLANNING_REGISTRY["emitted_planning_artifact_version"]:
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

    if pm_planning_record["planning_scope"] != PM_PLANNING_REGISTRY["planning_scope"]:
        raise ValueError("invalid planning_scope")

    if pm_planning_record["plan_class"] not in PM_PLANNING_REGISTRY["approved_plan_classes"]:
        raise ValueError("invalid plan_class")

    if pm_planning_record["next_step_class"] not in PM_PLANNING_REGISTRY["approved_next_step_classes"]:
        raise ValueError("invalid next_step_class")

    if pm_planning_record["plan_priority"] not in PM_PLANNING_REGISTRY["approved_plan_priority_values"]:
        raise ValueError("invalid plan_priority")

    required_flags = PM_PLANNING_REGISTRY["required_output_flags"]
    for field_name, expected_value in required_flags.items():
        if pm_planning_record.get(field_name) is not expected_value:
            raise ValueError(f"invalid output flag: {field_name}")

    supporting_counts = pm_planning_record.get("supporting_counts", {})
    _require_dict(supporting_counts, "supporting_counts")
    for key in ("continuity_count", "accepted_matches", "quarantined_matches", "analog_matches"):
        value = supporting_counts.get(key)
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"supporting_counts.{key} must be a non-negative int")