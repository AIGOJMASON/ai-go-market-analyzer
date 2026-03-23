"""
Policy helpers for Stage 73 execution fusion.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

from .execution_fusion_registry import (
    APPROVED_CHILD_CORE_HANDOFF,
    APPROVED_DOWNSTREAM_STATUS,
    APPROVED_INPUT_ARTIFACT_TYPES,
    FORBIDDEN_INTERNAL_KEYS,
    REQUIRED_EXECUTION_STATE_KEYS,
)


def _has_forbidden_keys(payload: Dict[str, Any]) -> Tuple[bool, str]:
    for key in payload:
        if key in FORBIDDEN_INTERNAL_KEYS:
            return True, key
    return False, ""


def _validate_common_execution_state(
    payload: Dict[str, Any],
    *,
    label: str,
    required_type: str,
) -> None:
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a dict")

    has_forbidden, key = _has_forbidden_keys(payload)
    if has_forbidden:
        raise ValueError(f"{label} contains forbidden internal key: {key}")

    missing = [key for key in REQUIRED_EXECUTION_STATE_KEYS if key not in payload]
    if missing:
        raise ValueError(f"{label} missing required keys: {missing}")

    if payload.get("artifact_type") != required_type:
        raise ValueError(
            f"{label} artifact_type must be {required_type}, got {payload.get('artifact_type')}"
        )

    if payload.get("sealed") is not True:
        raise ValueError(f"{label} must be sealed")

    weight = payload.get("authorized_weight")
    if not isinstance(weight, (int, float)):
        raise ValueError(f"{label} authorized_weight must be numeric")
    if weight < 0 or weight > 1:
        raise ValueError(f"{label} authorized_weight must be between 0 and 1 inclusive")

    entry_count = payload.get("refinement_entry_count")
    if not isinstance(entry_count, int):
        raise ValueError(f"{label} refinement_entry_count must be an int")
    if entry_count < 0:
        raise ValueError(f"{label} refinement_entry_count must be non-negative")

    if payload.get("downstream_status") not in APPROVED_DOWNSTREAM_STATUS:
        raise ValueError(f"{label} downstream_status is not approved")


def validate_rosetta_execution_state(payload: Dict[str, Any]) -> None:
    _validate_common_execution_state(
        payload,
        label="rosetta_runtime_execution_state",
        required_type=APPROVED_INPUT_ARTIFACT_TYPES["rosetta"],
    )

    if payload.get("runtime_mode") != "rosetta_refined_runtime":
        raise ValueError("rosetta_runtime_execution_state runtime_mode is invalid")


def validate_curved_mirror_execution_state(payload: Dict[str, Any]) -> None:
    _validate_common_execution_state(
        payload,
        label="curved_mirror_runtime_execution_state",
        required_type=APPROVED_INPUT_ARTIFACT_TYPES["curved_mirror"],
    )

    if payload.get("runtime_mode") != "curved_mirror_refined_runtime":
        raise ValueError("curved_mirror_runtime_execution_state runtime_mode is invalid")


def validate_case_continuity(
    rosetta_state: Dict[str, Any],
    curved_mirror_state: Dict[str, Any],
) -> None:
    if rosetta_state["case_id"] != curved_mirror_state["case_id"]:
        raise ValueError("execution states must share the same case_id")


def validate_combined_weight(
    rosetta_state: Dict[str, Any],
    curved_mirror_state: Dict[str, Any],
) -> None:
    total = float(rosetta_state["authorized_weight"]) + float(
        curved_mirror_state["authorized_weight"]
    )
    if total > 1.000001:
        raise ValueError("combined authorized weight may not exceed 1.0")


def build_execution_fusion_record(
    rosetta_state: Dict[str, Any],
    curved_mirror_state: Dict[str, Any],
) -> Dict[str, Any]:
    downstream_status = "ready_for_child_core"
    child_core_handoff = "fused_execution_ready"

    if downstream_status not in APPROVED_DOWNSTREAM_STATUS:
        raise ValueError("downstream_status not approved")

    if child_core_handoff not in APPROVED_CHILD_CORE_HANDOFF:
        raise ValueError("child_core_handoff not approved")

    return {
        "artifact_type": "execution_fusion_record",
        "sealed": True,
        "case_id": rosetta_state["case_id"],
        "source_rosetta_artifact_type": rosetta_state["artifact_type"],
        "source_curved_mirror_artifact_type": curved_mirror_state["artifact_type"],
        "weights": {
            "rosetta_weight": float(rosetta_state["authorized_weight"]),
            "curved_mirror_weight": float(curved_mirror_state["authorized_weight"]),
        },
        "runtime_modes": {
            "rosetta_mode": rosetta_state["runtime_mode"],
            "curved_mirror_mode": curved_mirror_state["runtime_mode"],
        },
        "entry_counts": {
            "rosetta_entries": int(rosetta_state["refinement_entry_count"]),
            "curved_mirror_entries": int(curved_mirror_state["refinement_entry_count"]),
        },
        "downstream_status": downstream_status,
        "child_core_handoff": child_core_handoff,
        "notes": (
            "Stage 73 fuses Rosetta and Curved Mirror runtime execution states "
            "without scoring, arbitration, or reweighting."
        ),
    }