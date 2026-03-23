"""
Policy helpers for Stage 77 target-specific adapter surface.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

from .target_specific_adapter_surface_registry import (
    APPROVED_ADAPTER_CLASSES,
    APPROVED_ADAPTER_STATUS,
    APPROVED_CHILD_CORE_TARGETS,
    APPROVED_DOWNSTREAM_STATUS,
    APPROVED_INPUT_ARTIFACT_TYPE,
    APPROVED_TARGET_SPECIFIC_STATUS,
    FORBIDDEN_INTERNAL_KEYS,
    REQUIRED_PACKET_KEYS,
    REQUIRED_RUNTIME_MODE_KEYS,
    REQUIRED_WEIGHT_KEYS,
    TARGET_TO_ADAPTER_CLASS,
    TARGET_TO_SURFACE_CLASS,
)


def _has_forbidden_keys(payload: Dict[str, Any]) -> Tuple[bool, str]:
    for key in payload:
        if key in FORBIDDEN_INTERNAL_KEYS:
            return True, key
    return False, ""


def validate_adapter_packet(payload: Dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise ValueError("child_core_adapter_packet must be a dict")

    has_forbidden, key = _has_forbidden_keys(payload)
    if has_forbidden:
        raise ValueError(f"child_core_adapter_packet contains forbidden internal key: {key}")

    missing = [key for key in REQUIRED_PACKET_KEYS if key not in payload]
    if missing:
        raise ValueError(f"child_core_adapter_packet missing required keys: {missing}")

    if payload.get("artifact_type") != APPROVED_INPUT_ARTIFACT_TYPE:
        raise ValueError(
            "child_core_adapter_packet artifact_type must be "
            f"{APPROVED_INPUT_ARTIFACT_TYPE}, got {payload.get('artifact_type')}"
        )

    if payload.get("sealed") is not True:
        raise ValueError("child_core_adapter_packet must be sealed")

    if payload.get("source_artifact_type") != "child_core_execution_result":
        raise ValueError("child_core_adapter_packet source_artifact_type is invalid")

    target = payload.get("child_core_target")
    if target not in APPROVED_CHILD_CORE_TARGETS:
        raise ValueError(f"child_core_target is not approved: {target}")

    adapter_class = payload.get("adapter_class")
    if adapter_class not in APPROVED_ADAPTER_CLASSES:
        raise ValueError(f"adapter_class is not approved: {adapter_class}")

    expected_adapter_class = TARGET_TO_ADAPTER_CLASS[target]
    if adapter_class != expected_adapter_class:
        raise ValueError("adapter_class does not match approved target mapping")

    if payload.get("adapter_status") not in APPROVED_ADAPTER_STATUS:
        raise ValueError("child_core_adapter_packet adapter_status is not approved")

    if payload.get("downstream_status") not in APPROVED_DOWNSTREAM_STATUS:
        raise ValueError("child_core_adapter_packet downstream_status is not approved")

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


def build_target_specific_adapter_packet(
    adapter_packet: Dict[str, Any],
) -> Dict[str, Any]:
    target = adapter_packet["child_core_target"]
    target_surface_class = TARGET_TO_SURFACE_CLASS[target]
    adapter_status = "ready_for_target_implementation"

    if adapter_status not in APPROVED_TARGET_SPECIFIC_STATUS:
        raise ValueError("adapter_status is not approved for target-specific output")

    return {
        "artifact_type": "target_specific_adapter_packet",
        "sealed": True,
        "case_id": adapter_packet["case_id"],
        "source_artifact_type": adapter_packet["artifact_type"],
        "child_core_target": target,
        "adapter_class": adapter_packet["adapter_class"],
        "target_surface_class": target_surface_class,
        "weights": {
            "rosetta_weight": float(adapter_packet["weights"]["rosetta_weight"]),
            "curved_mirror_weight": float(adapter_packet["weights"]["curved_mirror_weight"]),
        },
        "runtime_modes": {
            "rosetta_mode": adapter_packet["runtime_modes"]["rosetta_mode"],
            "curved_mirror_mode": adapter_packet["runtime_modes"]["curved_mirror_mode"],
        },
        "adapter_status": adapter_status,
        "downstream_status": adapter_packet["downstream_status"],
        "notes": (
            "Stage 77 converts one lawful child-core adapter packet into one bounded "
            "target_specific_adapter_packet without scoring, arbitration, reweighting, "
            "or hidden target specialization logic."
        ),
    }