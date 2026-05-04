from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from AI_GO.core.governance.governed_persistence import (
    build_authority_metadata,
    governed_write_raw_json,
)


ROOT = Path(__file__).resolve().parents[2]
TRANSITIONS_PATH = ROOT / "state" / "monitoring" / "current" / "transitions.json"

TRANSITIONS_MUTATION_CLASS = "monitoring_transition_persistence"
TRANSITIONS_PERSISTENCE_TYPE = "runtime_transition_log"
TRANSITIONS_ADVISORY_ONLY = True


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if isinstance(payload, dict) and payload.get("artifact_type") == "governed_persistence_envelope":
        inner = payload.get("payload", default)
        return inner if isinstance(inner, dict) else default

    return payload if isinstance(payload, dict) else default


def _authority_metadata(path: Path) -> Dict[str, Any]:
    return build_authority_metadata(
        authority_id="core_monitoring_transitions",
        operation="record_transition",
        actor="system",
        source="AI_GO.core.monitoring.transitions",
        extra={
            "target_path": str(path),
            "advisory_only": TRANSITIONS_ADVISORY_ONLY,
        },
    )


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    mutation_class = TRANSITIONS_MUTATION_CLASS
    persistence_type = TRANSITIONS_PERSISTENCE_TYPE
    advisory_only = TRANSITIONS_ADVISORY_ONLY
    authority_metadata = _authority_metadata(path)

    governed_payload = dict(payload)
    governed_payload.setdefault("classification", {
        "mutation_class": mutation_class,
        "persistence_type": persistence_type,
        "advisory_only": advisory_only,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "recommendation_mutation_allowed": False,
        "pm_authority_mutation_allowed": False,
    })
    governed_payload.setdefault("authority_metadata", authority_metadata)
    governed_payload.setdefault("sealed", True)

    governed_write_raw_json(
        path=path,
        payload=governed_payload,
        mutation_class=mutation_class,
        persistence_type=persistence_type,
        authority_metadata=authority_metadata,
        advisory_only=advisory_only,
    )


def _default_transitions() -> Dict[str, Any]:
    return {
        "transition_log_id": "AI_GO_RUNTIME_TRANSITIONS",
        "updated_at": _utc_now(),
        "items": [],
        "advisory_only": TRANSITIONS_ADVISORY_ONLY,
    }


def record_transition(packet_id: str, phase: str, status: str, details: Dict[str, Any] | None = None) -> str:
    log = _read_json(TRANSITIONS_PATH, _default_transitions())
    item = {
        "packet_id": packet_id,
        "phase": phase,
        "status": status,
        "details": details or {},
        "recorded_at": _utc_now(),
    }
    log.setdefault("items", [])
    log["items"].append(item)
    log["updated_at"] = _utc_now()
    log["advisory_only"] = TRANSITIONS_ADVISORY_ONLY
    _write_json(TRANSITIONS_PATH, log)
    return TRANSITIONS_PATH.as_posix()