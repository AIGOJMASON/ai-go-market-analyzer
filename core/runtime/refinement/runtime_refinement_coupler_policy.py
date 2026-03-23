"""
Policy helpers for Stage 70 runtime refinement coupling.

This module enforces:
- sealed artifact validation
- allocation bounds
- cross-consumer isolation
- case continuity
- lawful channel construction

This layer does NOT:
- score
- arbitrate
- reweight
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Tuple

from .runtime_refinement_coupler_registry import (
    APPROVED_INPUT_ARTIFACT_TYPES,
    APPROVED_ROUTE_TARGETS,
    FORBIDDEN_INTERNAL_KEYS,
    REQUIRED_ALLOCATION_KEYS,
    REQUIRED_RECEIPT_KEYS,
)


# ---------------------------------------------------------
# INTERNAL VALIDATION HELPERS
# ---------------------------------------------------------


def _has_forbidden_keys(payload: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Detect forbidden internal keys that must never leak into runtime artifacts.
    """
    for key in payload:
        if key in FORBIDDEN_INTERNAL_KEYS:
            return True, key
    return False, ""


def validate_common_artifact(
    payload: Dict[str, Any],
    *,
    required_type: str,
    required_keys: Iterable[str],
    label: str,
) -> None:
    """
    Shared validation logic for all Stage 70 inputs.
    """
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a dict")

    has_forbidden, key = _has_forbidden_keys(payload)
    if has_forbidden:
        raise ValueError(f"{label} contains forbidden internal key: {key}")

    missing = [key for key in required_keys if key not in payload]
    if missing:
        raise ValueError(f"{label} missing required keys: {missing}")

    if payload.get("artifact_type") != required_type:
        raise ValueError(
            f"{label} artifact_type must be {required_type}, got {payload.get('artifact_type')}"
        )

    if payload.get("sealed") is not True:
        raise ValueError(f"{label} must be sealed")


# ---------------------------------------------------------
# ALLOCATION VALIDATION
# ---------------------------------------------------------


def validate_allocation(payload: Dict[str, Any]) -> None:
    """
    Validate the upstream arbitrator allocation artifact.
    """
    validate_common_artifact(
        payload,
        required_type=APPROVED_INPUT_ARTIFACT_TYPES["allocation"],
        required_keys=REQUIRED_ALLOCATION_KEYS,
        label="engine_allocation_record",
    )

    rosetta_weight = payload.get("rosetta_weight")
    curved_mirror_weight = payload.get("curved_mirror_weight")

    for name, value in (
        ("rosetta_weight", rosetta_weight),
        ("curved_mirror_weight", curved_mirror_weight),
    ):
        if not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be numeric")

        if value < 0 or value > 1:
            raise ValueError(f"{name} must be between 0 and 1 inclusive")

    total = float(rosetta_weight) + float(curved_mirror_weight)

    # Strict upper bound enforcement
    if total > 1.000001:
        raise ValueError("combined engine weights may not exceed 1.0")


# ---------------------------------------------------------
# RECEIPT VALIDATION
# ---------------------------------------------------------


def validate_rosetta_receipt(payload: Dict[str, Any]) -> None:
    """
    Validate Rosetta refinement receipt.
    """
    validate_common_artifact(
        payload,
        required_type=APPROVED_INPUT_ARTIFACT_TYPES["rosetta_receipt"],
        required_keys=REQUIRED_RECEIPT_KEYS,
        label="rosetta_refinement_receipt",
    )

    # Prevent cross-consumer leakage
    if "curved_mirror_signals" in payload:
        raise ValueError(
            "rosetta_refinement_receipt may not contain curved_mirror_signals"
        )


def validate_curved_mirror_receipt(payload: Dict[str, Any]) -> None:
    """
    Validate Curved Mirror refinement receipt.
    """
    validate_common_artifact(
        payload,
        required_type=APPROVED_INPUT_ARTIFACT_TYPES["curved_mirror_receipt"],
        required_keys=REQUIRED_RECEIPT_KEYS,
        label="curved_mirror_refinement_receipt",
    )

    # Prevent cross-consumer leakage
    if "rosetta_guidance" in payload:
        raise ValueError(
            "curved_mirror_refinement_receipt may not contain rosetta_guidance"
        )


# ---------------------------------------------------------
# CONTINUITY VALIDATION
# ---------------------------------------------------------


def validate_case_continuity(
    allocation: Dict[str, Any],
    rosetta_receipt: Dict[str, Any],
    curved_mirror_receipt: Dict[str, Any],
) -> None:
    """
    Ensure all artifacts refer to the same case.
    """
    case_id = allocation["case_id"]

    if rosetta_receipt["case_id"] != case_id:
        raise ValueError(
            "rosetta_refinement_receipt case_id does not match allocation"
        )

    if curved_mirror_receipt["case_id"] != case_id:
        raise ValueError(
            "curved_mirror_refinement_receipt case_id does not match allocation"
        )


# ---------------------------------------------------------
# CHANNEL BUILDERS
# ---------------------------------------------------------


def build_rosetta_channel(
    allocation: Dict[str, Any],
    rosetta_receipt: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Construct Rosetta runtime channel.
    """
    return {
        "authorized_weight": float(allocation["rosetta_weight"]),
        "route_target": APPROVED_ROUTE_TARGETS["rosetta"],
        "receipt_artifact_type": rosetta_receipt["artifact_type"],
        "entry_count": len(rosetta_receipt.get("entries", [])),
        "sealed_receipt": True,
    }


def build_curved_mirror_channel(
    allocation: Dict[str, Any],
    curved_mirror_receipt: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Construct Curved Mirror runtime channel.
    """
    return {
        "authorized_weight": float(allocation["curved_mirror_weight"]),
        "route_target": APPROVED_ROUTE_TARGETS["curved_mirror"],
        "receipt_artifact_type": curved_mirror_receipt["artifact_type"],
        "entry_count": len(curved_mirror_receipt.get("entries", [])),
        "sealed_receipt": True,
    }