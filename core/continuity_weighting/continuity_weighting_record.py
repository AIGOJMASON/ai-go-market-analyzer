from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from AI_GO.core.governance.governed_persistence import governed_write_json


MUTATION_CLASS = "memory_persistence"
PERSISTENCE_TYPE = "continuity_weighting_record"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_mutate_workflow_state": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "continuity_weighting_memory_only",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _state_path() -> Path:
    return _project_root() / "state" / "smi" / "current" / "smi_state.json"


def _ledger_path() -> Path:
    return _project_root() / "state" / "smi" / "current" / "change_ledger.json"


def _output_path() -> Path:
    return _project_root() / "state" / "continuity_weighting" / "current" / "continuity_weighting_record.json"


def _read_json(path: Path, default: Dict[str, Any]) -> Dict[str, Any]:
    if not path.exists():
        return dict(default)

    payload = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(payload, dict):
        raise ValueError(f"{path} must decode to a dict")

    return payload


def _pattern_status(count: int) -> Dict[str, Any]:
    if count <= 1:
        return {"pattern_status": "emerging", "weight": 0.25}
    if count == 2:
        return {"pattern_status": "strengthening", "weight": 0.50}
    if count in {3, 4}:
        return {"pattern_status": "active", "weight": 0.75}
    return {"pattern_status": "dominant", "weight": 1.00}


def _build_ranked_patterns(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    continuity_keys = state.get("continuity_keys", {})
    if not isinstance(continuity_keys, dict):
        return []

    patterns: List[Dict[str, Any]] = []

    for key, value in continuity_keys.items():
        if not isinstance(value, dict):
            continue

        recurrence_count = _safe_int(value.get("recurrence_count"), 1)
        status_rule = _pattern_status(recurrence_count)

        patterns.append(
            {
                "continuity_key": str(value.get("continuity_key") or key),
                "recurrence_count": recurrence_count,
                "last_seen_timestamp": value.get("last_seen_timestamp"),
                "source_surface": value.get("source_surface", "unknown"),
                "event_class": value.get("event_class", "unknown"),
                "symbol": value.get("symbol", ""),
                "event_theme": value.get("event_theme", ""),
                "weight": status_rule["weight"],
                "pattern_status": status_rule["pattern_status"],
            }
        )

    patterns.sort(
        key=lambda item: (
            float(item.get("weight", 0.0)),
            _safe_int(item.get("recurrence_count"), 0),
        ),
        reverse=True,
    )
    return patterns


def _normalize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(record)
    normalized["artifact_type"] = "continuity_weighting_record"
    normalized["artifact_version"] = "v1"
    normalized["persistence_type"] = PERSISTENCE_TYPE
    normalized["mutation_class"] = MUTATION_CLASS
    normalized["advisory_only"] = True
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    return normalized


def _governed_write(path: Path, payload: Dict[str, Any]) -> Any:
    normalized = _normalize_record(payload)

    kwargs = {
        "path": path,
        "output_path": path,
        "payload": normalized,
        "data": normalized,
        "persistence_type": PERSISTENCE_TYPE,
        "mutation_class": MUTATION_CLASS,
        "advisory_only": True,
        "authority_metadata": dict(AUTHORITY_METADATA),
    }

    signature = inspect.signature(governed_write_json)
    accepted = {
        key: value
        for key, value in kwargs.items()
        if key in signature.parameters
    }

    if any(parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in signature.parameters.values()):
        return governed_write_json(**kwargs)

    if accepted:
        return governed_write_json(**accepted)

    return governed_write_json(path, normalized)


def build_continuity_weighting_record(persist: bool = True) -> Dict[str, Any]:
    state = _read_json(_state_path(), {"continuity_keys": {}})
    ledger = _read_json(_ledger_path(), {"changes": []})

    ranked_patterns = _build_ranked_patterns(state)
    timestamp = _utc_now()

    top_pattern = ranked_patterns[0] if ranked_patterns else {}

    record = _normalize_record(
        {
            "record_id": f"continuity_weighting_{timestamp.replace(':', '-')}",
            "timestamp": timestamp,
            "source_state_path": str(_state_path().relative_to(_project_root())),
            "source_ledger_path": str(_ledger_path().relative_to(_project_root())),
            "total_accepted_events": len(ledger.get("changes", []))
            if isinstance(ledger.get("changes"), list)
            else 0,
            "total_continuity_keys": len(ranked_patterns),
            "ranked_patterns": ranked_patterns,
            "summary": {
                "top_pattern_key": top_pattern.get("continuity_key"),
                "top_pattern_status": top_pattern.get("pattern_status"),
                "top_pattern_weight": top_pattern.get("weight"),
                "change_ledger_entries": len(ledger.get("changes", []))
                if isinstance(ledger.get("changes"), list)
                else 0,
            },
        }
    )

    if persist:
        result = _governed_write(_output_path(), record)
        record["path"] = str(
            result.get("path")
            if isinstance(result, dict) and result.get("path")
            else _output_path()
        )

    return record