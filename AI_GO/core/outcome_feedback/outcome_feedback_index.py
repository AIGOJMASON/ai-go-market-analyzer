
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.state_runtime.state_paths import state_root


OUTCOME_INDEX_VERSION = "northstar_outcome_index_v1"
STATE_ROOT = state_root() / "outcome_feedback"

MUTATION_CLASS = "outcome_index_persistence"
PERSISTENCE_TYPE = "outcome_feedback_index"
ADVISORY_ONLY = True


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": PERSISTENCE_TYPE,
        "mutation_class": MUTATION_CLASS,
        "execution_allowed": False,
        "state_mutation_allowed": False,
        "workflow_mutation_allowed": False,
        "project_truth_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "advisory_only": ADVISORY_ONLY,
        "governed_persistence": True,
    }


def _authority_block() -> Dict[str, Any]:
    return {
        "authority_id": "core_outcome_feedback_index",
        "operation": "write_outcome_feedback_index",
        "source": "AI_GO.core.outcome_feedback.outcome_feedback_index",
        "actor": "system",
        "advisory_only": ADVISORY_ONLY,
        "can_execute": False,
        "can_mutate_operational_state": False,
        "can_mutate_workflow_state": False,
        "can_mutate_project_truth": False,
        "can_mutate_pm_authority": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
        "can_override_state_authority": False,
        "can_override_cross_core_integrity": False,
        "authority_scope": "outcome_feedback_index_only",
        "governed_persistence": True,
    }


def get_outcome_feedback_index_path() -> Path:
    return STATE_ROOT / "current" / "outcome_feedback_index.json"


def _empty_index() -> Dict[str, Any]:
    return {
        "artifact_type": "outcome_feedback_index",
        "artifact_version": OUTCOME_INDEX_VERSION,
        "status": "empty",
        "updated_at": "",
        "generated_at": _utc_now_iso(),
        "entry_count": 0,
        "latest_entry_id": None,
        "entries": [],
        "records": [],
        "persistence_type": PERSISTENCE_TYPE,
        "mutation_class": MUTATION_CLASS,
        "advisory_only": ADVISORY_ONLY,
        "classification": _classification_block(),
        "authority": _authority_block(),
        "authority_metadata": _authority_block(),
        "sealed": True,
    }


def _unwrap_governed_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    if (
        isinstance(payload, dict)
        and payload.get("artifact_type") == "governed_persistence_envelope"
        and isinstance(payload.get("payload"), dict)
    ):
        return dict(payload["payload"])

    return payload


def read_outcome_feedback_index() -> Dict[str, Any]:
    path = get_outcome_feedback_index_path()

    if not path.exists():
        return _empty_index()

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _empty_index()

    if not isinstance(payload, dict):
        return _empty_index()

    payload = _unwrap_governed_payload(payload)

    entries = payload.get("entries", payload.get("records", []))
    if not isinstance(entries, list):
        entries = []

    payload.setdefault("artifact_type", "outcome_feedback_index")
    payload.setdefault("artifact_version", OUTCOME_INDEX_VERSION)
    payload.setdefault("classification", _classification_block())
    payload.setdefault("authority", _authority_block())
    payload.setdefault("authority_metadata", _authority_block())
    payload.setdefault("sealed", True)

    payload["persistence_type"] = PERSISTENCE_TYPE
    payload["mutation_class"] = MUTATION_CLASS
    payload["advisory_only"] = ADVISORY_ONLY
    payload["entries"] = entries
    payload["records"] = entries
    payload["entry_count"] = int(payload.get("entry_count", len(entries)) or len(entries))
    payload["latest_entry_id"] = payload.get("latest_entry_id")

    return payload


def write_outcome_feedback_index(index_payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(index_payload, dict):
        raise ValueError("index_payload must be a dict")

    payload = dict(index_payload)
    entries = payload.get("entries", payload.get("records", []))
    if not isinstance(entries, list):
        entries = []

    authority_metadata = _authority_block()

    payload["artifact_type"] = "outcome_feedback_index"
    payload["artifact_version"] = OUTCOME_INDEX_VERSION
    payload["status"] = "active" if entries else "empty"
    payload["updated_at"] = _utc_now_iso()
    payload["entry_count"] = len(entries)
    payload["entries"] = entries
    payload["records"] = entries
    payload["persistence_type"] = PERSISTENCE_TYPE
    payload["mutation_class"] = MUTATION_CLASS
    payload["advisory_only"] = ADVISORY_ONLY
    payload["classification"] = _classification_block()
    payload["authority"] = authority_metadata
    payload["authority_metadata"] = authority_metadata
    payload["sealed"] = True

    path = get_outcome_feedback_index_path()
    result = governed_write_json(
        path=path,
        payload=payload,
        mutation_class=MUTATION_CLASS,
        persistence_type=PERSISTENCE_TYPE,
        authority_metadata=authority_metadata,
        advisory_only=ADVISORY_ONLY,
    )

    return {
        "status": "persisted",
        "artifact_type": "outcome_feedback_index_write",
        "persistence_type": PERSISTENCE_TYPE,
        "mutation_class": MUTATION_CLASS,
        "path": str(result.get("path") if isinstance(result, dict) and result.get("path") else path),
        "entry_count": len(entries),
        "latest_entry_id": payload.get("latest_entry_id"),
        "classification": _classification_block(),
        "authority": authority_metadata,
        "authority_metadata": authority_metadata,
        "sealed": True,
    }


def _build_entry(record: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(record, dict):
        raise ValueError("record must be a dict")

    core_id = _safe_str(record.get("core_id")) or "unknown"
    closeout_id = _safe_str(record.get("closeout_id")) or "unknown"
    entry_id = _safe_str(record.get("entry_id")) or f"outcome_feedback_{core_id}_{closeout_id}"

    return {
        "entry_id": entry_id,
        "indexed_at": _utc_now_iso(),
        "core_id": core_id,
        "closeout_id": closeout_id,
        "symbol": record.get("symbol"),
        "event_theme": record.get("event_theme"),
        "expected_behavior": record.get("expected_behavior"),
        "actual_outcome": record.get("actual_outcome"),
        "outcome_class": record.get("outcome_class"),
        "delta_pct": record.get("delta_pct"),
        "record_id": record.get("record_id"),
        "persistence_type": "outcome_feedback_index_entry",
        "mutation_class": MUTATION_CLASS,
        "advisory_only": ADVISORY_ONLY,
        "classification": _classification_block(),
        "authority": _authority_block(),
        "authority_metadata": _authority_block(),
        "sealed": True,
    }


def append_outcome_feedback_index(record: Dict[str, Any]) -> Dict[str, Any]:
    index_payload = read_outcome_feedback_index()
    entries: List[Dict[str, Any]] = [
        dict(item) for item in index_payload.get("entries", []) if isinstance(item, dict)
    ]

    entry = _build_entry(record)
    entry_id = _safe_str(entry.get("entry_id"))

    entries = [
        existing
        for existing in entries
        if _safe_str(existing.get("entry_id")) != entry_id
    ]
    entries.append(entry)

    index_payload["entries"] = entries
    index_payload["records"] = entries
    index_payload["latest_entry_id"] = entry_id

    persistence = write_outcome_feedback_index(index_payload)

    return {
        "status": "indexed",
        "artifact_type": "outcome_feedback_index_append",
        "entry": entry,
        "entry_id": entry_id,
        "index_path": persistence["path"],
        "entry_count": persistence["entry_count"],
        "classification": _classification_block(),
        "authority": _authority_block(),
        "authority_metadata": _authority_block(),
        "sealed": True,
    }
