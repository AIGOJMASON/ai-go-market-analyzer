"""
Policy helpers for Stage 76 child-core adapter layer.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

from .child_core_adapter_registry import (
    APPROVED_ADAPTER_STATUS,
    APPROVED_CHILD_CORE_TARGETS,
    APPROVED_DOWNSTREAM_STATUS,
    APPROVED_EXECUTION_STATUS,
    APPROVED_INPUT_ARTIFACT_TYPE,
    FORBIDDEN_INTERNAL_KEYS,
    REQUIRED_RESULT_KEYS,
    REQUIRED_RUNTIME_MODE_KEYS,
    REQUIRED_WEIGHT_KEYS,
    TARGET_TO_ADAPTER_CLASS,
)


def _has_forbidden_keys(payload: Dict[str, Any]) -> Tuple[bool, str]:
    for key in payload:
        if key in FORBIDDEN_INTERNAL_KEYS:
            return True, key
    return False, ""


def validate_execution_result(payload: Dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise ValueError("child_core_execution_result must be a dict")

    has_forbidden, key = _has_forbidden_keys(payload)
    if has_forbidden:
        raise ValueError(f"child_core_execution_result contains forbidden internal key: {key}")

    missing = [key for key in REQUIRED_RESULT_KEYS if key not in payload]
    if missing:
        raise ValueError(f"child_core_execution_result missing required keys: {missing}")

    if payload.get("artifact_type") != APPROVED_INPUT_ARTIFACT_TYPE:
        raise ValueError(
            "child_core_execution_result artifact_type must be "
            f"{APPROVED_INPUT_ARTIFACT_TYPE}, got {payload.get('artifact_type')}"
        )

    if payload.get("sealed") is not True:
        raise ValueError("child_core_execution_result must be sealed")

    if payload.get("source_artifact_type") != "child_core_execution_packet":
        raise ValueError("child_core_execution_result source_artifact_type is invalid")

    target = payload.get("child_core_target")
    if target not in APPROVED_CHILD_CORE_TARGETS:
        raise ValueError(f"child_core_target is not approved: {target}")

    if payload.get("execution_status") not in APPROVED_EXECUTION_STATUS:
        raise ValueError("child_core_execution_result execution_status is not approved")

    if payload.get("downstream_status") not in APPROVED_DOWNSTREAM_STATUS:
        raise ValueError("child_core_execution_result downstream_status is not approved")

    weights = payload.get("weights")
    if not isinstance(weights, dict):
        raise ValueError("weights must be a dict")

    missing_weight_keys = [key for key in REQUIRED_WEIGHT_KEYS if key not in weights]
    if missing_weight_keys:
        raise ValueError(f"weights missing required keys: {missing_weight_keys}")

    rosetta_weight = weights.get("rosetta_weight")
    curved_mirror_weight = weights.get("curved_mirror_weight")

    for name, value in (
        ("rosetta_weight", rosetta_weight),
        ("curved_mirror_weight", curved_mirror_weight),
    ):
        if not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be numeric")
        if value < 0 or value > 1:
            raise ValueError(f"{name} must be between 0 and 1 inclusive")

    if float(rosetta_weight) + float(curved_mirror_weight) > 1.000001:
        raise ValueError("combined weights may not exceed 1.0")

    runtime_modes = payload.get("runtime_modes")
    if not isinstance(runtime_modes, dict):
        raise ValueError("runtime_modes must be a dict")

    missing_runtime_keys = [key for key in REQUIRED_RUNTIME_MODE_KEYS if key not in runtime_modes]
    if missing_runtime_keys:
        raise ValueError(f"runtime_modes missing required keys: {missing_runtime_keys}")

    if runtime_modes.get("rosetta_mode") != "rosetta_refined_runtime":
        raise ValueError("runtime_modes rosetta_mode is invalid")

    if runtime_modes.get("curved_mirror_mode") != "curved_mirror_refined_runtime":
        raise ValueError("runtime_modes curved_mirror_mode is invalid")


def resolve_adapter_class(child_core_target: str) -> str:
    if child_core_target not in TARGET_TO_ADAPTER_CLASS:
        raise ValueError(f"No adapter class defined for child_core_target: {child_core_target}")
    return TARGET_TO_ADAPTER_CLASS[child_core_target]


def build_child_core_adapter_packet(
    execution_result: Dict[str, Any],
) -> Dict[str, Any]:
    child_core_target = execution_result["child_core_target"]
    adapter_class = resolve_adapter_class(child_core_target)
    adapter_status = "ready_for_target_adapter"

    if adapter_status not in APPROVED_ADAPTER_STATUS:
        raise ValueError("adapter_status is not approved")

    return {
        "artifact_type": "child_core_adapter_packet",
        "sealed": True,
        "case_id": execution_result["case_id"],
        "source_artifact_type": execution_result["artifact_type"],
        "child_core_target": child_core_target,
        "adapter_class": adapter_class,
        "weights": {
            "rosetta_weight": float(execution_result["weights"]["rosetta_weight"]),
            "curved_mirror_weight": float(execution_result["weights"]["curved_mirror_weight"]),
        },
        "runtime_modes": {
            "rosetta_mode": execution_result["runtime_modes"]["rosetta_mode"],
            "curved_mirror_mode": execution_result["runtime_modes"]["curved_mirror_mode"],
        },
        "adapter_status": adapter_status,
        "downstream_status": execution_result["downstream_status"],
        "notes": (
            "Stage 76 converts one lawful child-core execution result into one bounded "
            "child_core_adapter_packet without scoring, arbitration, reweighting, "
            "or hidden adapter selection."
        ),
    }