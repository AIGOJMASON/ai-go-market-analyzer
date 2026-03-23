from __future__ import annotations

from typing import Any, Dict

from .output_registry import OUTPUT_TARGETS


REQUIRED_OUTPUT_FIELDS = [
    "artifact_id",
    "artifact_type",
    "originating_core",
    "validation_receipt_ref",
    "lifecycle_state",
    "timestamp",
    "summary",
]


def validate_output(artifact: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that an artifact is eligible for output-layer exposure.

    Returns a structured validation result so probes can inspect failure reasons.
    """
    missing_fields = [field for field in REQUIRED_OUTPUT_FIELDS if field not in artifact]
    if missing_fields:
        return {
            "ok": False,
            "reason": "missing_required_fields",
            "missing_fields": missing_fields,
        }

    if artifact.get("lifecycle_state") != "CLOSED":
        return {
            "ok": False,
            "reason": "artifact_not_closed",
            "lifecycle_state": artifact.get("lifecycle_state"),
        }

    if not artifact.get("validation_receipt_ref"):
        return {
            "ok": False,
            "reason": "missing_validation_receipt_ref",
        }

    return {"ok": True}


def expose_to_watcher(artifact: Dict[str, Any]) -> Dict[str, Any]:
    """
    Expose an artifact to the watcher surface if it passes output validation
    and is allowed by watcher registry policy.
    """
    validation_result = validate_output(artifact)
    if not validation_result["ok"]:
        raise ValueError(f"Artifact failed output validation: {validation_result}")

    watcher_profile = OUTPUT_TARGETS["watcher"]
    allowed_artifacts = watcher_profile["allowed_artifacts"]

    if artifact["artifact_type"] not in allowed_artifacts:
        raise ValueError(
            f"Artifact type not allowed for watcher: {artifact['artifact_type']}"
        )

    return artifact