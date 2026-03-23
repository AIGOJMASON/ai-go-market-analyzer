from __future__ import annotations

from typing import Any, Dict

from core.monitoring.verification import (
    load_json_artifact,
    verify_artifact_exists,
    verify_research_packet_shape,
)


def verify_research_packet_artifact(packet_path: str) -> Dict[str, Any]:
    """
    Verify that a persisted research packet exists and matches the expected
    governed packet shape.

    This watcher is a thin verification surface.
    It does not create packets, mutate packets, or perform continuity writes.
    """
    existence_result = verify_artifact_exists(packet_path)

    if not existence_result["exists"] or not existence_result["is_file"]:
        return {
            "status": "failed",
            "artifact_type": "research_packet",
            "packet_path": packet_path,
            "existence_check": existence_result,
            "shape_check": None,
            "error": {
                "type": "artifact_missing",
                "message": "Research packet artifact does not exist as a file.",
            },
        }

    try:
        artifact_payload = load_json_artifact(packet_path)
    except Exception as exc:
        return {
            "status": "failed",
            "artifact_type": "research_packet",
            "packet_path": packet_path,
            "existence_check": existence_result,
            "shape_check": None,
            "error": {
                "type": exc.__class__.__name__,
                "message": str(exc),
            },
        }

    shape_result = verify_research_packet_shape(artifact_payload)

    return {
        "status": "verified" if shape_result["shape_valid"] else "failed",
        "artifact_type": "research_packet",
        "packet_path": packet_path,
        "existence_check": existence_result,
        "shape_check": shape_result,
        "error": None if shape_result["shape_valid"] else {
            "type": "shape_validation_failed",
            "message": "Research packet artifact failed governed shape validation.",
        },
    }