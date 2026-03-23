from __future__ import annotations

import importlib
from copy import deepcopy
from uuid import uuid4

from AI_GO.core.runtime.refinement.child_core_execution_surface_registry import (
    APPROVED_CHILD_CORE_TARGETS,
    APPROVED_DOWNSTREAM_STATUS_VALUES,
    APPROVED_EXECUTION_STATUS_VALUES,
    APPROVED_INPUT_ARTIFACT_TYPE,
    APPROVED_OUTPUT_ARTIFACT_TYPE,
    APPROVED_INTAKE_VALUES,
    FORBIDDEN_INTERNAL_FIELDS,
    REQUIRED_PACKET_KEYS,
    REQUIRED_RUNTIME_MODE_KEYS,
    REQUIRED_WEIGHT_KEYS,
)


class ChildCoreExecutionSurfaceError(ValueError):
    """Raised when Stage 75 execution-surface validation fails."""


def _as_dict(value) -> dict:
    return value if isinstance(value, dict) else {}


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise ChildCoreExecutionSurfaceError(message)


def _validate_no_forbidden_fields(packet: dict) -> None:
    leaked = FORBIDDEN_INTERNAL_FIELDS.intersection(packet.keys())
    _assert(not leaked, f"forbidden internal fields present: {sorted(leaked)}")


def validate_child_core_execution_packet(packet: dict) -> None:
    _assert(isinstance(packet, dict), "child_core_execution_packet must be a dict")
    _assert(
        packet.get("artifact_type") == APPROVED_INPUT_ARTIFACT_TYPE,
        f"artifact_type must be {APPROVED_INPUT_ARTIFACT_TYPE}",
    )
    _assert(packet.get("sealed") is True, "child_core_execution_packet must be sealed")

    missing_packet_keys = REQUIRED_PACKET_KEYS.difference(packet.keys())
    _assert(not missing_packet_keys, f"missing packet keys: {sorted(missing_packet_keys)}")

    target_core = packet.get("target_core")
    _assert(
        target_core in APPROVED_CHILD_CORE_TARGETS,
        f"target_core must be one of {sorted(APPROVED_CHILD_CORE_TARGETS)}",
    )

    _assert(
        packet.get("intake_status") in APPROVED_INTAKE_VALUES,
        f"intake_status must be one of {sorted(APPROVED_INTAKE_VALUES)}",
    )

    runtime_mode = _as_dict(packet.get("runtime_mode"))
    missing_runtime = REQUIRED_RUNTIME_MODE_KEYS.difference(runtime_mode.keys())
    _assert(not missing_runtime, f"missing runtime_mode keys: {sorted(missing_runtime)}")

    combined_weights = _as_dict(packet.get("combined_weights"))
    missing_weights = REQUIRED_WEIGHT_KEYS.difference(combined_weights.keys())
    _assert(not missing_weights, f"missing combined_weights keys: {sorted(missing_weights)}")

    for key in REQUIRED_WEIGHT_KEYS:
        value = combined_weights.get(key)
        _assert(isinstance(value, (int, float)), f"combined_weights.{key} must be numeric")
        _assert(0.0 <= float(value) <= 1.0, f"combined_weights.{key} must be between 0.0 and 1.0")

    _assert(isinstance(packet.get("child_core_payload"), dict), "child_core_payload must be a dict")
    _validate_no_forbidden_fields(packet)


def resolve_executor(target_core: str):
    meta = APPROVED_CHILD_CORE_TARGETS[target_core]
    module = importlib.import_module(meta["executor_module"])
    fn = getattr(module, meta["executor_fn"])
    return fn


def _build_market_analyzer_runtime_packet(packet: dict) -> dict:
    """
    Stage 75 must feed market_analyzer_v1 the same envelope shape it already
    accepts from its validated packet contract.
    """
    child_core_payload = deepcopy(packet["child_core_payload"])

    runtime_packet = {
        "artifact_type": "pm_decision_packet",
        "dispatched_by": "PM_CORE",
        "target_core": "market_analyzer_v1",
        "dispatch_id": packet["packet_id"],
        "source": "validated_upstream",
        "receipt": {
            "receipt_id": packet["packet_id"],
        },
        "payload": child_core_payload,
    }
    return runtime_packet


def _execute_target(packet: dict):
    target_core = packet["target_core"]
    executor = resolve_executor(target_core)

    if target_core == "market_analyzer_v1":
        runtime_packet = _build_market_analyzer_runtime_packet(packet)
        return executor(runtime_packet)

    raise ChildCoreExecutionSurfaceError(
        f"no Stage 75 execution mapping implemented for target_core={target_core}"
    )


def build_child_core_execution_result(packet: dict) -> dict:
    validate_child_core_execution_packet(packet)

    target_core = packet["target_core"]

    execution_status = "succeeded"
    downstream_status = "ready_for_adapter"
    runtime_error = None

    try:
        runtime_result = _execute_target(packet)
    except Exception as error:
        runtime_result = None
        runtime_error = str(error)
        execution_status = "rejected"
        downstream_status = "execution_rejected"

    _assert(
        execution_status in APPROVED_EXECUTION_STATUS_VALUES,
        "invalid execution_status during result construction",
    )
    _assert(
        downstream_status in APPROVED_DOWNSTREAM_STATUS_VALUES,
        "invalid downstream_status during result construction",
    )

    result_id = f"CCER-{uuid4().hex[:16].upper()}"

    result = {
        "artifact_type": APPROVED_OUTPUT_ARTIFACT_TYPE,
        "sealed": True,
        "result_id": result_id,
        "source_artifact_type": APPROVED_INPUT_ARTIFACT_TYPE,
        "source_lineage": {
            "packet_id": packet.get("packet_id"),
            "source_lineage": packet.get("source_lineage"),
        },
        "target_core": target_core,
        "execution_status": execution_status,
        "downstream_status": downstream_status,
        "runtime_mode": deepcopy(packet.get("runtime_mode", {})),
        "combined_weights": deepcopy(packet.get("combined_weights", {})),
        "execution_artifacts": runtime_result,
        "runtime_error": runtime_error,
        "receipt": {
            "receipt_type": "child_core_execution_surface_receipt",
            "target_core": target_core,
            "result_id": result_id,
        },
    }
    return result