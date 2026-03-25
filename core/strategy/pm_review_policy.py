from AI_GO.core.strategy.pm_review_registry import PM_REVIEW_REGISTRY


def _require_dict(value, field_name: str) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be a dict")


def _require_non_empty_string(value, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _ensure_no_forbidden_fields(payload: dict) -> None:
    forbidden = set(PM_REVIEW_REGISTRY["forbidden_internal_fields"])
    for key in payload.keys():
        if key in forbidden or key.startswith("_"):
            raise ValueError(f"forbidden internal field present: {key}")


def validate_pm_strategy_record(pm_strategy_record: dict) -> None:
    _require_dict(pm_strategy_record, "pm_strategy_record")
    _ensure_no_forbidden_fields(pm_strategy_record)

    if pm_strategy_record.get("artifact_type") != PM_REVIEW_REGISTRY["accepted_strategy_artifact_type"]:
        raise ValueError("invalid pm strategy artifact_type")

    if pm_strategy_record.get("artifact_version") != PM_REVIEW_REGISTRY["accepted_strategy_artifact_version"]:
        raise ValueError("invalid pm strategy artifact_version")

    if pm_strategy_record.get("sealed") is not True:
        raise ValueError("pm_strategy_record must be sealed")

    for key in (
        "strategy_id",
        "core_id",
        "strategy_scope",
        "source_record_id",
        "source_index_id",
        "continuity_key",
        "signal_class",
        "arbitration_class",
        "strategy_class",
        "continuity_strength",
        "trend_direction",
        "pm_guidance",
    ):
        _require_non_empty_string(pm_strategy_record.get(key), key)

    if pm_strategy_record["strategy_scope"] != "pm_guidance_only":
        raise ValueError("invalid strategy_scope")

    required_flags = PM_REVIEW_REGISTRY["required_input_flags"]
    for field_name, expected_value in required_flags.items():
        if pm_strategy_record.get(field_name) is not expected_value:
            raise ValueError(f"invalid strategy input flag: {field_name}")

    supporting_counts = pm_strategy_record.get("supporting_counts", {})
    _require_dict(supporting_counts, "supporting_counts")
    for key in ("continuity_count", "accepted_matches", "quarantined_matches", "analog_matches"):
        value = supporting_counts.get(key)
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"supporting_counts.{key} must be a non-negative int")


def classify_review_class(pm_strategy_record: dict) -> str:
    strategy_class = pm_strategy_record["strategy_class"]

    if strategy_class == "escalate_for_pm_review":
        return "escalate"
    if strategy_class == "elevated_caution":
        return "review"
    if strategy_class == "reinforced_support":
        return "plan"
    if strategy_class == "monitor":
        return "observe"
    if strategy_class == "insufficient_pattern":
        return "observe"

    raise ValueError("unsupported strategy_class")


def classify_review_priority(pm_strategy_record: dict) -> str:
    strategy_class = pm_strategy_record["strategy_class"]
    continuity_strength = pm_strategy_record["continuity_strength"]

    if strategy_class == "escalate_for_pm_review":
        return "high"
    if strategy_class == "elevated_caution":
        return "high" if continuity_strength == "high" else "medium"
    if strategy_class == "reinforced_support":
        return "medium"
    return "low"


def build_review_summary(pm_strategy_record: dict, review_class: str, review_priority: str) -> str:
    signal_class = pm_strategy_record["signal_class"]
    strategy_class = pm_strategy_record["strategy_class"]
    continuity_strength = pm_strategy_record["continuity_strength"]
    trend_direction = pm_strategy_record["trend_direction"]

    if review_class == "escalate":
        return (
            f"PM review escalation recommended for {signal_class}. "
            f"Strategy class={strategy_class}, strength={continuity_strength}, trend={trend_direction}."
        )
    if review_class == "review":
        return (
            f"PM review recommended for {signal_class} due to {strategy_class}. "
            f"Priority={review_priority}, strength={continuity_strength}, trend={trend_direction}."
        )
    if review_class == "plan":
        return (
            f"PM planning posture is appropriate for {signal_class}. "
            f"Strategy class={strategy_class}, strength={continuity_strength}, trend={trend_direction}."
        )
    return (
        f"PM should continue observation for {signal_class}. "
        f"Strategy class={strategy_class}, priority={review_priority}."
    )


def build_review_payload(pm_strategy_record: dict, review_id: str) -> dict:
    review_class = classify_review_class(pm_strategy_record)
    review_priority = classify_review_priority(pm_strategy_record)

    payload = {
        "artifact_type": PM_REVIEW_REGISTRY["emitted_review_artifact_type"],
        "artifact_version": PM_REVIEW_REGISTRY["emitted_review_artifact_version"],
        "sealed": True,
        "review_id": review_id,
        "core_id": pm_strategy_record["core_id"],
        "review_scope": PM_REVIEW_REGISTRY["review_scope"],
        "source_strategy_id": pm_strategy_record["strategy_id"],
        "continuity_key": pm_strategy_record["continuity_key"],
        "signal_class": pm_strategy_record["signal_class"],
        "strategy_class": pm_strategy_record["strategy_class"],
        "review_class": review_class,
        "review_priority": review_priority,
        "review_summary": build_review_summary(
            pm_strategy_record=pm_strategy_record,
            review_class=review_class,
            review_priority=review_priority,
        ),
        "supporting_counts": dict(pm_strategy_record["supporting_counts"]),
        "memory_only": True,
        "runtime_mutation_allowed": False,
        "execution_influence": False,
        "recommendation_mutation_allowed": False,
    }
    return payload


def validate_output_review(pm_review_record: dict) -> None:
    _require_dict(pm_review_record, "pm_review_record")
    _ensure_no_forbidden_fields(pm_review_record)

    if pm_review_record.get("artifact_type") != PM_REVIEW_REGISTRY["emitted_review_artifact_type"]:
        raise ValueError("invalid pm review artifact_type")

    if pm_review_record.get("artifact_version") != PM_REVIEW_REGISTRY["emitted_review_artifact_version"]:
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

    if pm_review_record["review_scope"] != PM_REVIEW_REGISTRY["review_scope"]:
        raise ValueError("invalid review_scope")

    if pm_review_record["review_class"] not in PM_REVIEW_REGISTRY["approved_review_classes"]:
        raise ValueError("invalid review_class")

    if pm_review_record["review_priority"] not in PM_REVIEW_REGISTRY["approved_review_priority_values"]:
        raise ValueError("invalid review_priority")

    required_flags = PM_REVIEW_REGISTRY["required_output_flags"]
    for field_name, expected_value in required_flags.items():
        if pm_review_record.get(field_name) is not expected_value:
            raise ValueError(f"invalid output flag: {field_name}")

    supporting_counts = pm_review_record.get("supporting_counts", {})
    _require_dict(supporting_counts, "supporting_counts")
    for key in ("continuity_count", "accepted_matches", "quarantined_matches", "analog_matches"):
        value = supporting_counts.get(key)
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"supporting_counts.{key} must be a non-negative int")