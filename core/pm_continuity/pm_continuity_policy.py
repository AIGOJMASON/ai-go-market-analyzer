from copy import deepcopy

from AI_GO.core.pm_continuity.pm_continuity_registry import PM_CONTINUITY_REGISTRY


def _require_dict(value, field_name: str) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be a dict")


def _require_non_empty_string(value, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _ensure_no_forbidden_fields(payload: dict) -> None:
    forbidden = set(PM_CONTINUITY_REGISTRY["forbidden_internal_fields"])
    for key in payload.keys():
        if key in forbidden or key.startswith("_"):
            raise ValueError(f"forbidden internal field present: {key}")


def validate_refinement_packet(refinement_packet: dict) -> None:
    _require_dict(refinement_packet, "refinement_packet")
    _ensure_no_forbidden_fields(refinement_packet)

    _require_non_empty_string(refinement_packet.get("artifact_type"), "artifact_type")
    _require_non_empty_string(
        refinement_packet.get("artifact_version"),
        "artifact_version",
    )
    _require_non_empty_string(refinement_packet.get("case_id"), "case_id")
    _require_non_empty_string(refinement_packet.get("core_id"), "core_id")
    _require_non_empty_string(
        refinement_packet.get("signal_class"),
        "signal_class",
    )
    _require_non_empty_string(
        refinement_packet.get("arbitration_class"),
        "arbitration_class",
    )
    _require_non_empty_string(
        refinement_packet.get("confidence_adjustment"),
        "confidence_adjustment",
    )

    if refinement_packet["artifact_type"] != PM_CONTINUITY_REGISTRY["accepted_input_artifact_type"]:
        raise ValueError("invalid refinement artifact_type")

    if refinement_packet["artifact_version"] != PM_CONTINUITY_REGISTRY["accepted_input_artifact_version"]:
        raise ValueError("invalid refinement artifact_version")

    if refinement_packet.get("sealed") is not True:
        raise ValueError("refinement_packet must be sealed")

    required_flags = PM_CONTINUITY_REGISTRY["required_refinement_flags"]
    for field_name, expected_value in required_flags.items():
        if refinement_packet.get(field_name) is not expected_value:
            raise ValueError(f"invalid refinement flag: {field_name}")

    risk_flags = refinement_packet.get("risk_flags", [])
    if not isinstance(risk_flags, list):
        raise ValueError("risk_flags must be a list")

    source_summary = refinement_packet.get("source_summary", {})
    _require_dict(source_summary, "source_summary")

    for key in ("accepted_matches", "quarantined_matches", "analog_matches"):
        value = source_summary.get(key)
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"source_summary.{key} must be a non-negative int")


def validate_existing_index(index_payload: dict) -> None:
    _require_dict(index_payload, "index_payload")
    _ensure_no_forbidden_fields(index_payload)

    if index_payload.get("artifact_type") != PM_CONTINUITY_REGISTRY["emitted_index_artifact_type"]:
        raise ValueError("invalid index artifact_type")

    if index_payload.get("artifact_version") != PM_CONTINUITY_REGISTRY["emitted_index_artifact_version"]:
        raise ValueError("invalid index artifact_version")

    if index_payload.get("sealed") is not True:
        raise ValueError("pm_continuity_index must be sealed")

    entries = index_payload.get("entries", [])
    if not isinstance(entries, list):
        raise ValueError("entries must be a list")

    for entry in entries:
        validate_index_entry(entry)


def validate_index_entry(entry: dict) -> None:
    _require_dict(entry, "index_entry")
    _ensure_no_forbidden_fields(entry)

    for key in PM_CONTINUITY_REGISTRY["approved_index_key_fields"]:
        _require_non_empty_string(entry.get(key), key)

    count = entry.get("continuity_count")
    if not isinstance(count, int) or count < 1:
        raise ValueError("continuity_count must be a positive int")

    _require_non_empty_string(entry.get("last_case_id"), "last_case_id")
    _require_non_empty_string(entry.get("last_record_id"), "last_record_id")


def build_continuity_key(refinement_packet: dict) -> str:
    parts = [
        refinement_packet["core_id"],
        refinement_packet["signal_class"],
        refinement_packet["arbitration_class"],
        refinement_packet["confidence_adjustment"],
    ]
    return "::".join(parts)


def build_base_record(
    refinement_packet: dict,
    record_id: str,
    continuity_key: str,
) -> dict:
    risk_flags = deepcopy(refinement_packet.get("risk_flags", []))
    source_summary = deepcopy(refinement_packet.get("source_summary", {}))

    record = {
        "artifact_type": PM_CONTINUITY_REGISTRY["emitted_record_artifact_type"],
        "artifact_version": PM_CONTINUITY_REGISTRY["emitted_record_artifact_version"],
        "sealed": True,
        "record_id": record_id,
        "case_id": refinement_packet["case_id"],
        "core_id": refinement_packet["core_id"],
        "source_artifact_type": refinement_packet["artifact_type"],
        "source_artifact_version": refinement_packet["artifact_version"],
        "source_refinement_case_id": refinement_packet["case_id"],
        "continuity_key": continuity_key,
        "signal_class": refinement_packet["signal_class"],
        "arbitration_class": refinement_packet["arbitration_class"],
        "confidence_adjustment": refinement_packet["confidence_adjustment"],
        "risk_flags": risk_flags,
        "source_summary": source_summary,
        "memory_only": True,
        "runtime_mutation_allowed": False,
        "execution_influence": False,
        "recommendation_mutation_allowed": False,
    }
    return record


def validate_output_record(record_payload: dict) -> None:
    _require_dict(record_payload, "record_payload")
    _ensure_no_forbidden_fields(record_payload)

    if record_payload.get("artifact_type") != PM_CONTINUITY_REGISTRY["emitted_record_artifact_type"]:
        raise ValueError("invalid continuity record artifact_type")

    if record_payload.get("artifact_version") != PM_CONTINUITY_REGISTRY["emitted_record_artifact_version"]:
        raise ValueError("invalid continuity record artifact_version")

    if record_payload.get("sealed") is not True:
        raise ValueError("continuity record must be sealed")

    for key in (
        "record_id",
        "case_id",
        "core_id",
        "source_artifact_type",
        "source_artifact_version",
        "source_refinement_case_id",
        "continuity_key",
        "signal_class",
        "arbitration_class",
        "confidence_adjustment",
    ):
        _require_non_empty_string(record_payload.get(key), key)

    required_output_flags = PM_CONTINUITY_REGISTRY["required_output_flags"]
    for field_name, expected_value in required_output_flags.items():
        if record_payload.get(field_name) is not expected_value:
            raise ValueError(f"invalid output flag: {field_name}")

    if record_payload.get("execution_influence") is not False:
        raise ValueError("execution_influence must remain false")

    if record_payload.get("recommendation_mutation_allowed") is not False:
        raise ValueError("recommendation_mutation_allowed must remain false")

    if not isinstance(record_payload.get("risk_flags", []), list):
        raise ValueError("risk_flags must be a list")

    source_summary = record_payload.get("source_summary", {})
    _require_dict(source_summary, "source_summary")


def build_empty_index(index_id: str) -> dict:
    return {
        "artifact_type": PM_CONTINUITY_REGISTRY["emitted_index_artifact_type"],
        "artifact_version": PM_CONTINUITY_REGISTRY["emitted_index_artifact_version"],
        "sealed": True,
        "index_id": index_id,
        "entry_count": 0,
        "entries": [],
        "memory_only": True,
        "runtime_mutation_allowed": False,
    }


def validate_output_index(index_payload: dict) -> None:
    validate_existing_index(index_payload)

    _require_non_empty_string(index_payload.get("index_id"), "index_id")

    if index_payload.get("memory_only") is not True:
        raise ValueError("index memory_only must be true")

    if index_payload.get("runtime_mutation_allowed") is not False:
        raise ValueError("index runtime_mutation_allowed must be false")

    entry_count = index_payload.get("entry_count")
    entries = index_payload.get("entries", [])
    if not isinstance(entry_count, int) or entry_count != len(entries):
        raise ValueError("entry_count must match entries length")