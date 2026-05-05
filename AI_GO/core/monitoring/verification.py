from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable


RESEARCH_PACKET_REQUIRED_KEYS = [
    "packet_id",
    "packet_type",
    "issuing_authority",
    "created_at",
    "title",
    "summary",
    "source_refs",
    "scope",
    "tags",
    "intake_record",
    "screening_result",
    "trust_result",
]


def verify_artifact_exists(path: str | Path) -> Dict[str, Any]:
    artifact_path = Path(path)

    return {
        "artifact_type": "artifact_existence_verification",
        "artifact_version": "v1",
        "check": "artifact_exists",
        "path": str(artifact_path),
        "exists": artifact_path.exists(),
        "is_file": artifact_path.is_file(),
        "advisory_only": True,
        "can_execute": False,
        "can_mutate_workflow_state": False,
    }


def load_json_artifact(path: str | Path) -> Dict[str, Any]:
    artifact_path = Path(path)
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))

    if not isinstance(payload, dict):
        raise ValueError("Artifact JSON must decode to a dict at the top level")

    return payload


def verify_required_keys(payload: Dict[str, Any], required_keys: Iterable[str]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        return {
            "artifact_type": "required_key_verification",
            "artifact_version": "v1",
            "valid": False,
            "missing_keys": list(required_keys),
            "advisory_only": True,
            "can_execute": False,
            "can_mutate_workflow_state": False,
        }

    missing = [key for key in required_keys if key not in payload]

    return {
        "artifact_type": "required_key_verification",
        "artifact_version": "v1",
        "valid": not missing,
        "missing_keys": missing,
        "advisory_only": True,
        "can_execute": False,
        "can_mutate_workflow_state": False,
    }


def verify_research_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    result = verify_required_keys(payload, RESEARCH_PACKET_REQUIRED_KEYS)

    return {
        "artifact_type": "research_packet_verification",
        "artifact_version": "v1",
        "valid": result["valid"],
        "missing_keys": result["missing_keys"],
        "advisory_only": True,
        "can_execute": False,
        "can_mutate_workflow_state": False,
    }