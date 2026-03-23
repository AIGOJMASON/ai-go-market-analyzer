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
        "check": "artifact_exists",
        "path": str(artifact_path),
        "exists": artifact_path.exists(),
        "is_file": artifact_path.is_file(),
    }


def load_json_artifact(path: str | Path) -> Dict[str, Any]:
    artifact_path = Path(path)

    with artifact_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise ValueError("Artifact JSON must decode to a dict at the top level")

    return payload


def verify_required_keys(payload: Dict[str, Any], required_keys: Iterable[str]) -> Dict[str, Any]:
    required = list(required_keys)
    missing_keys = [key for key in required if key not in payload]

    return {
        "check": "required_keys",
        "required_keys": required,
        "missing_keys": missing_keys,
        "all_present": len(missing_keys) == 0,
    }


def verify_research_packet_shape(payload: Dict[str, Any]) -> Dict[str, Any]:
    key_result = verify_required_keys(payload, RESEARCH_PACKET_REQUIRED_KEYS)

    packet_type_ok = payload.get("packet_type") == "research_packet"
    authority_ok = payload.get("issuing_authority") == "RESEARCH_CORE"

    return {
        "check": "research_packet_shape",
        "all_present": key_result["all_present"],
        "missing_keys": key_result["missing_keys"],
        "packet_type_ok": packet_type_ok,
        "authority_ok": authority_ok,
        "shape_valid": (
            key_result["all_present"]
            and packet_type_ok
            and authority_ok
        ),
    }