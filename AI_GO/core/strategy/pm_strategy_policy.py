from copy import deepcopy

from AI_GO.core.strategy.pm_strategy_registry import PM_STRATEGY_REGISTRY


def _require_dict(value, field_name: str) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be a dict")


def _require_non_empty_string(value, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _ensure_no_forbidden_fields(payload: dict) -> None:
    forbidden = set(PM_STRATEGY_REGISTRY["forbidden_internal_fields"])
    for key in payload.keys():
        if key in forbidden or key.startswith("_"):
            raise ValueError(f"forbidden internal field present: {key}")


def validate_pm_continuity_record(pm_continuity_record: dict) -> None:
    _require_dict(pm_continuity_record, "pm_continuity_record")
    _ensure_no_forbidden_fields(pm_continuity_record)

    if pm_continuity_record.get("artifact_type") != PM_STRATEGY_REGISTRY["accepted_record_artifact_type"]:
        raise ValueError("invalid continuity record artifact_type")

    if pm_continuity_record.get("artifact_version") != PM_STRATEGY_REGISTRY["accepted_record_artifact_version"]:
        raise ValueError("invalid continuity record artifact_version")

    if pm_continuity_record.get("sealed") is not True:
        raise ValueError("pm_continuity_record must be sealed")

    for key in (
        "record_id",
        "case_id",
        "core_id",
        "continuity_key",
        "signal_class",
        "arbitration_class",
        "confidence_adjustment",
    ):
        _require_non_empty_string(pm_continuity_record.get(key), key)

    required_input_flags = PM_STRATEGY_REGISTRY["required_input_flags"]
    for field_name, expected_value in required_input_flags.items():
        if pm_continuity_record.get(field_name) is not expected_value:
            raise ValueError(f"invalid continuity record input flag: {field_name}")

    required_record_flags = PM_STRATEGY_REGISTRY["required_record_flags"]
    for field_name, expected_value in required_record_flags.items():
        if pm_continuity_record.get(field_name) is not expected_value:
            raise ValueError(f"invalid continuity record flag: {field_name}")

    risk_flags = pm_continuity_record.get("risk_flags", [])
    if not isinstance(risk_flags, list):
        raise ValueError("risk_flags must be a list")

    source_summary = pm_continuity_record.get("source_summary", {})
    _require_dict(source_summary, "source_summary")

    for key in ("accepted_matches", "quarantined_matches", "analog_matches"):
        value = source_summary.get(key)
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"source_summary.{key} must be a non-negative int")


def validate_pm_continuity_index(pm_continuity_index: dict) -> None:
    _require_dict(pm_continuity_index, "pm_continuity_index")
    _ensure_no_forbidden_fields(pm_continuity_index)

    if pm_continuity_index.get("artifact_type") != PM_STRATEGY_REGISTRY["accepted_index_artifact_type"]:
        raise ValueError("invalid continuity index artifact_type")

    if pm_continuity_index.get("artifact_version") != PM_STRATEGY_REGISTRY["accepted_index_artifact_version"]:
        raise ValueError("invalid continuity index artifact_version")

    if pm_continuity_index.get("sealed") is not True:
        raise ValueError("pm_continuity_index must be sealed")

    _require_non_empty_string(pm_continuity_index.get("index_id"), "index_id")

    required_input_flags = PM_STRATEGY_REGISTRY["required_input_flags"]
    for field_name, expected_value in required_input_flags.items():
        if pm_continuity_index.get(field_name) is not expected_value:
            raise ValueError(f"invalid continuity index input flag: {field_name}")

    entry_count = pm_continuity_index.get("entry_count")
    entries = pm_continuity_index.get("entries", [])
    if not isinstance(entry_count, int) or entry_count < 0:
        raise ValueError("entry_count must be a non-negative int")
    if not isinstance(entries, list):
        raise ValueError("entries must be a list")
    if entry_count != len(entries):
        raise ValueError("entry_count must match entries length")

    for entry in entries:
        validate_index_entry(entry)


def validate_index_entry(entry: dict) -> None:
    _require_dict(entry, "index_entry")
    _ensure_no_forbidden_fields(entry)

    for key in (
        "continuity_key",
        "core_id",
        "signal_class",
        "arbitration_class",
        "confidence_adjustment",
        "last_case_id",
        "last_record_id",
    ):
        _require_non_empty_string(entry.get(key), key)

    continuity_count = entry.get("continuity_count")
    if not isinstance(continuity_count, int) or continuity_count < 1:
        raise ValueError("continuity_count must be a positive int")


def _find_matching_index_entry(
    pm_continuity_record: dict,
    pm_continuity_index: dict,
) -> dict | None:
    continuity_key = pm_continuity_record["continuity_key"]
    for entry in pm_continuity_index.get("entries", []):
        if entry["continuity_key"] == continuity_key:
            return deepcopy(entry)
    return None


def classify_continuity_strength(continuity_count: int) -> str:
    if continuity_count >= 4:
        return "high"
    if continuity_count >= 2:
        return "medium"
    return "low"


def classify_trend_direction(
    pm_continuity_record: dict,
    pm_continuity_index: dict,
    matching_entry: dict | None,
) -> str:
    if matching_entry is None:
        return "insufficient_data"

    continuity_count = matching_entry["continuity_count"]
    entries = pm_continuity_index.get("entries", [])
    same_signal_entries = [
        entry
        for entry in entries
        if entry["core_id"] == pm_continuity_record["core_id"]
        and entry["signal_class"] == pm_continuity_record["signal_class"]
    ]

    if len(same_signal_entries) > 1:
        arbitration_classes = {entry["arbitration_class"] for entry in same_signal_entries}
        if len(arbitration_classes) > 1:
            return "branching"

    if continuity_count <= 1:
        return "insufficient_data"

    accepted_matches = pm_continuity_record["source_summary"]["accepted_matches"]
    quarantined_matches = pm_continuity_record["source_summary"]["quarantined_matches"]
    if accepted_matches > 0 and quarantined_matches > 0:
        return "mixed"

    return "reinforcing"


def classify_strategy_class(
    pm_continuity_record: dict,
    matching_entry: dict | None,
    continuity_strength: str,
    trend_direction: str,
) -> str:
    if trend_direction == "branching":
        return "monitor"

    if matching_entry is None or matching_entry["continuity_count"] <= 1:
        return "insufficient_pattern"

    arbitration_class = pm_continuity_record["arbitration_class"]
    accepted_matches = pm_continuity_record["source_summary"]["accepted_matches"]
    quarantined_matches = pm_continuity_record["source_summary"]["quarantined_matches"]

    if arbitration_class == "cautionary":
        if continuity_strength == "high" and quarantined_matches >= accepted_matches:
            return "escalate_for_pm_review"
        return "elevated_caution"

    if arbitration_class == "supportive":
        return "reinforced_support"

    if arbitration_class == "neutral":
        return "monitor"

    return "monitor"


def build_pm_guidance(
    pm_continuity_record: dict,
    strategy_class: str,
    continuity_strength: str,
    trend_direction: str,
    continuity_count: int,
) -> str:
    signal_class = pm_continuity_record["signal_class"]
    arbitration_class = pm_continuity_record["arbitration_class"]

    if strategy_class == "insufficient_pattern":
        return (
            f"Continuity for {signal_class} remains too sparse for durable PM posture; "
            f"continue monitoring without strategy escalation."
        )

    if strategy_class == "elevated_caution":
        return (
            f"Repeated {arbitration_class} continuity for {signal_class} suggests PM should "
            f"treat similar cases as elevated-risk. Strength={continuity_strength}, "
            f"trend={trend_direction}, continuity_count={continuity_count}."
        )

    if strategy_class == "reinforced_support":
        return (
            f"Repeated supportive continuity for {signal_class} suggests PM may treat "
            f"similar cases as structurally reinforced under current governed conditions. "
            f"Strength={continuity_strength}, trend={trend_direction}, continuity_count={continuity_count}."
        )

    if strategy_class == "escalate_for_pm_review":
        return (
            f"High-strength cautionary continuity for {signal_class} now warrants PM review. "
            f"Repeated adverse continuity exceeds normal monitoring posture."
        )

    return (
        f"Continuity for {signal_class} is evolving across multiple posture branches. "
        f"PM should monitor pattern divergence before formal escalation."
    )


def build_supporting_counts(
    pm_continuity_record: dict,
    continuity_count: int,
) -> dict:
    source_summary = pm_continuity_record["source_summary"]
    return {
        "continuity_count": continuity_count,
        "accepted_matches": source_summary["accepted_matches"],
        "quarantined_matches": source_summary["quarantined_matches"],
        "analog_matches": source_summary["analog_matches"],
    }


def build_strategy_payload(
    pm_continuity_record: dict,
    pm_continuity_index: dict,
    strategy_id: str,
) -> dict:
    matching_entry = _find_matching_index_entry(pm_continuity_record, pm_continuity_index)
    continuity_count = matching_entry["continuity_count"] if matching_entry else 0
    continuity_strength = classify_continuity_strength(continuity_count)
    trend_direction = classify_trend_direction(
        pm_continuity_record=pm_continuity_record,
        pm_continuity_index=pm_continuity_index,
        matching_entry=matching_entry,
    )
    strategy_class = classify_strategy_class(
        pm_continuity_record=pm_continuity_record,
        matching_entry=matching_entry,
        continuity_strength=continuity_strength,
        trend_direction=trend_direction,
    )

    payload = {
        "artifact_type": PM_STRATEGY_REGISTRY["emitted_strategy_artifact_type"],
        "artifact_version": PM_STRATEGY_REGISTRY["emitted_strategy_artifact_version"],
        "sealed": True,
        "strategy_id": strategy_id,
        "core_id": pm_continuity_record["core_id"],
        "strategy_scope": PM_STRATEGY_REGISTRY["strategy_scope"],
        "source_record_id": pm_continuity_record["record_id"],
        "source_index_id": pm_continuity_index["index_id"],
        "continuity_key": pm_continuity_record["continuity_key"],
        "signal_class": pm_continuity_record["signal_class"],
        "arbitration_class": pm_continuity_record["arbitration_class"],
        "strategy_class": strategy_class,
        "continuity_strength": continuity_strength,
        "trend_direction": trend_direction,
        "pm_guidance": build_pm_guidance(
            pm_continuity_record=pm_continuity_record,
            strategy_class=strategy_class,
            continuity_strength=continuity_strength,
            trend_direction=trend_direction,
            continuity_count=continuity_count,
        ),
        "supporting_counts": build_supporting_counts(
            pm_continuity_record=pm_continuity_record,
            continuity_count=continuity_count,
        ),
        "memory_only": True,
        "runtime_mutation_allowed": False,
        "execution_influence": False,
        "recommendation_mutation_allowed": False,
    }
    return payload


def validate_output_strategy(pm_strategy_record: dict) -> None:
    _require_dict(pm_strategy_record, "pm_strategy_record")
    _ensure_no_forbidden_fields(pm_strategy_record)

    if pm_strategy_record.get("artifact_type") != PM_STRATEGY_REGISTRY["emitted_strategy_artifact_type"]:
        raise ValueError("invalid pm strategy artifact_type")

    if pm_strategy_record.get("artifact_version") != PM_STRATEGY_REGISTRY["emitted_strategy_artifact_version"]:
        raise ValueError("invalid pm strategy artifact_version")

    if pm_strategy_record.get("sealed") is not True:
        raise ValueError("pm strategy record must be sealed")

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

    if pm_strategy_record["strategy_scope"] != PM_STRATEGY_REGISTRY["strategy_scope"]:
        raise ValueError("invalid strategy_scope")

    if pm_strategy_record["strategy_class"] not in PM_STRATEGY_REGISTRY["approved_strategy_classes"]:
        raise ValueError("invalid strategy_class")

    if pm_strategy_record["continuity_strength"] not in PM_STRATEGY_REGISTRY["approved_continuity_strength_values"]:
        raise ValueError("invalid continuity_strength")

    if pm_strategy_record["trend_direction"] not in PM_STRATEGY_REGISTRY["approved_trend_direction_values"]:
        raise ValueError("invalid trend_direction")

    required_output_flags = PM_STRATEGY_REGISTRY["required_output_flags"]
    for field_name, expected_value in required_output_flags.items():
        if pm_strategy_record.get(field_name) is not expected_value:
            raise ValueError(f"invalid output flag: {field_name}")

    supporting_counts = pm_strategy_record.get("supporting_counts", {})
    _require_dict(supporting_counts, "supporting_counts")
    for key in ("continuity_count", "accepted_matches", "quarantined_matches", "analog_matches"):
        value = supporting_counts.get(key)
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"supporting_counts.{key} must be a non-negative int")