from __future__ import annotations

from copy import deepcopy
from uuid import uuid4

from AI_GO.core.runtime.refinement.child_core_execution_intake_registry import (
    APPROVED_CHILD_CORE_TARGETS,
    APPROVED_DOWNSTREAM_STATUS_VALUES,
    APPROVED_HANDOFF_POSTURE_VALUES,
    APPROVED_INPUT_ARTIFACT_TYPE,
    APPROVED_INTAKE_STATUS_VALUES,
    APPROVED_OUTPUT_ARTIFACT_TYPE,
    FORBIDDEN_INTERNAL_FIELDS,
    REQUIRED_FUSION_KEYS,
    REQUIRED_RUNTIME_MODE_KEYS,
    REQUIRED_WEIGHT_KEYS,
)


class ChildCoreExecutionIntakeError(ValueError):
    """Raised when Stage 74 intake validation fails."""


def _as_dict(value) -> dict:
    return value if isinstance(value, dict) else {}


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise ChildCoreExecutionIntakeError(message)


def _validate_no_forbidden_fields(record: dict) -> None:
    leaked = FORBIDDEN_INTERNAL_FIELDS.intersection(record.keys())
    _assert(not leaked, f"forbidden internal fields present: {sorted(leaked)}")


def validate_execution_fusion_record(execution_fusion_record: dict) -> None:
    _assert(isinstance(execution_fusion_record, dict), "execution_fusion_record must be a dict")
    _assert(
        execution_fusion_record.get("artifact_type") == APPROVED_INPUT_ARTIFACT_TYPE,
        f"artifact_type must be {APPROVED_INPUT_ARTIFACT_TYPE}",
    )
    _assert(execution_fusion_record.get("sealed") is True, "execution_fusion_record must be sealed")

    missing_keys = REQUIRED_FUSION_KEYS.difference(execution_fusion_record.keys())
    _assert(not missing_keys, f"missing required fusion keys: {sorted(missing_keys)}")

    runtime_mode = _as_dict(execution_fusion_record.get("runtime_mode"))
    missing_runtime_mode = REQUIRED_RUNTIME_MODE_KEYS.difference(runtime_mode.keys())
    _assert(not missing_runtime_mode, f"missing runtime_mode keys: {sorted(missing_runtime_mode)}")

    combined_weights = _as_dict(execution_fusion_record.get("combined_weights"))
    missing_weights = REQUIRED_WEIGHT_KEYS.difference(combined_weights.keys())
    _assert(not missing_weights, f"missing combined_weights keys: {sorted(missing_weights)}")

    for key in REQUIRED_WEIGHT_KEYS:
        value = combined_weights.get(key)
        _assert(isinstance(value, (int, float)), f"combined_weights.{key} must be numeric")
        _assert(0.0 <= float(value) <= 1.0, f"combined_weights.{key} must be between 0.0 and 1.0")

    handoff_posture = execution_fusion_record.get("child_core_handoff")
    _assert(
        handoff_posture in APPROVED_HANDOFF_POSTURE_VALUES,
        f"child_core_handoff must be one of {sorted(APPROVED_HANDOFF_POSTURE_VALUES)}",
    )

    _validate_no_forbidden_fields(execution_fusion_record)


def validate_child_core_target(target_core: str) -> None:
    _assert(isinstance(target_core, str) and target_core, "target_core is required")
    _assert(
        target_core in APPROVED_CHILD_CORE_TARGETS,
        f"target_core must be one of {sorted(APPROVED_CHILD_CORE_TARGETS)}",
    )


def resolve_child_core_payload(execution_fusion_record: dict, target_core: str) -> dict:
    """
    Stage 74 resolves the downstream child-core payload from the fused record.

    Lawful sources, in order:
    1. child_core_payloads[target_core]
    2. child_core_payload
    3. payload
    """
    payloads = _as_dict(execution_fusion_record.get("child_core_payloads"))
    if target_core in payloads:
        payload = payloads[target_core]
    elif "child_core_payload" in execution_fusion_record:
        payload = execution_fusion_record.get("child_core_payload")
    else:
        payload = execution_fusion_record.get("payload")

    _assert(isinstance(payload, dict), "resolved child_core payload must be a dict")

    target_meta = APPROVED_CHILD_CORE_TARGETS[target_core]
    required_payload_type = target_meta.get("required_payload_type")
    if required_payload_type == "dict":
        _assert(isinstance(payload, dict), "target payload must be a dict")

    return deepcopy(payload)


def build_child_core_execution_packet(
    execution_fusion_record: dict,
    target_core: str,
) -> dict:
    validate_execution_fusion_record(execution_fusion_record)
    validate_child_core_target(target_core)

    child_core_payload = resolve_child_core_payload(execution_fusion_record, target_core)
    combined_weights = deepcopy(_as_dict(execution_fusion_record.get("combined_weights")))
    runtime_mode = deepcopy(_as_dict(execution_fusion_record.get("runtime_mode")))

    intake_status = "accepted"
    downstream_status = "ready_for_execution_surface"

    _assert(
        intake_status in APPROVED_INTAKE_STATUS_VALUES,
        "invalid intake_status during packet construction",
    )
    _assert(
        downstream_status in APPROVED_DOWNSTREAM_STATUS_VALUES,
        "invalid downstream_status during packet construction",
    )

    return {
        "artifact_type": APPROVED_OUTPUT_ARTIFACT_TYPE,
        "sealed": True,
        "packet_id": f"CCEP-{uuid4().hex[:16].upper()}",
        "source_artifact_type": APPROVED_INPUT_ARTIFACT_TYPE,
        "source_lineage": {
            "fusion_id": execution_fusion_record.get("fusion_id"),
            "source_receipt": execution_fusion_record.get("receipt"),
        },
        "target_core": target_core,
        "intake_status": intake_status,
        "downstream_status": downstream_status,
        "handoff_posture": execution_fusion_record.get("child_core_handoff"),
        "runtime_mode": runtime_mode,
        "combined_weights": combined_weights,
        "child_core_payload": child_core_payload,
        "receipt": {
            "receipt_type": "child_core_execution_intake_receipt",
            "target_core": target_core,
            "packet_id": None,  # filled below
        },
    }