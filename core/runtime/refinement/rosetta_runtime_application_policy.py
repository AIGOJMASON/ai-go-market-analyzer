"""
Policy helpers for Stage 71 Rosetta runtime application.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

from .rosetta_runtime_application_registry import (
    APPROVED_DOWNSTREAM_STATUS,
    APPROVED_INPUT_ARTIFACT_TYPE,
    APPROVED_ROUTE_TARGET,
    APPROVED_RUNTIME_MODES,
    FORBIDDEN_INTERNAL_KEYS,
    REQUIRED_INPUT_KEYS,
    REQUIRED_ROSETTA_CHANNEL_KEYS,
)


def _has_forbidden_keys(payload: Dict[str, Any]) -> Tuple[bool, str]:
    for key in payload:
        if key in FORBIDDEN_INTERNAL_KEYS:
            return True, key
    return False, ""


def validate_input(payload: Dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise ValueError("runtime_refinement_coupling_record must be a dict")

    has_forbidden, key = _has_forbidden_keys(payload)
    if has_forbidden:
        raise ValueError(f"runtime_refinement_coupling_record contains forbidden internal key: {key}")

    missing = [key for key in REQUIRED_INPUT_KEYS if key not in payload]
    if missing:
        raise ValueError(f"runtime_refinement_coupling_record missing required keys: {missing}")

    if payload.get("artifact_type") != APPROVED_INPUT_ARTIFACT_TYPE:
        raise ValueError(
            f"runtime_refinement_coupling_record artifact_type must be "
            f"{APPROVED_INPUT_ARTIFACT_TYPE}, got {payload.get('artifact_type')}"
        )

    if payload.get("sealed") is not True:
        raise ValueError("runtime_refinement_coupling_record must be sealed")


def validate_rosetta_channel(payload: Dict[str, Any]) -> None:
    rosetta_channel = payload.get("rosetta_channel")
    if not isinstance(rosetta_channel, dict):
        raise ValueError("rosetta_channel must be a dict")

    missing = [key for key in REQUIRED_ROSETTA_CHANNEL_KEYS if key not in rosetta_channel]
    if missing:
        raise ValueError(f"rosetta_channel missing required keys: {missing}")

    if rosetta_channel.get("route_target") != APPROVED_ROUTE_TARGET:
        raise ValueError("rosetta_channel route_target is invalid")

    if rosetta_channel.get("receipt_artifact_type") != "rosetta_refinement_receipt":
        raise ValueError("rosetta_channel receipt_artifact_type must be rosetta_refinement_receipt")

    if rosetta_channel.get("sealed_receipt") is not True:
        raise ValueError("rosetta_channel sealed_receipt must be True")

    weight = rosetta_channel.get("authorized_weight")
    if not isinstance(weight, (int, float)):
        raise ValueError("rosetta_channel authorized_weight must be numeric")
    if weight < 0 or weight > 1:
        raise ValueError("rosetta_channel authorized_weight must be between 0 and 1 inclusive")

    entry_count = rosetta_channel.get("entry_count")
    if not isinstance(entry_count, int):
        raise ValueError("rosetta_channel entry_count must be an int")
    if entry_count < 0:
        raise ValueError("rosetta_channel entry_count must be non-negative")


def validate_no_cross_consumer_leakage(payload: Dict[str, Any]) -> None:
    rosetta_channel = payload["rosetta_channel"]
    if "curved_mirror_signals" in rosetta_channel:
        raise ValueError("rosetta_channel may not contain curved_mirror_signals")

    curved_mirror_channel = payload.get("curved_mirror_channel")
    if isinstance(curved_mirror_channel, dict):
        if curved_mirror_channel.get("route_target") == APPROVED_ROUTE_TARGET:
            raise ValueError("curved_mirror_channel may not route to rosetta target")


def build_execution_state(
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    rosetta_channel = payload["rosetta_channel"]

    runtime_mode = "rosetta_refined_runtime"
    downstream_status = "ready_for_child_core"

    if runtime_mode not in APPROVED_RUNTIME_MODES:
        raise ValueError("runtime_mode not approved")
    if downstream_status not in APPROVED_DOWNSTREAM_STATUS:
        raise ValueError("downstream_status not approved")

    return {
        "artifact_type": "rosetta_runtime_execution_state",
        "sealed": True,
        "case_id": payload["case_id"],
        "source_artifact_type": payload["artifact_type"],
        "authorized_weight": float(rosetta_channel["authorized_weight"]),
        "refinement_entry_count": int(rosetta_channel["entry_count"]),
        "runtime_mode": runtime_mode,
        "downstream_status": downstream_status,
        "notes": (
            "Stage 71 applies Rosetta runtime refinement within authorized bounds "
            "without scoring, arbitration, or reweighting."
        ),
    }