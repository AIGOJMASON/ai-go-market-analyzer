from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from AI_GO.core.state_runtime.state_paths import resolve_contractor_project_root


GOVERNED_PERSISTENCE_ENVELOPE = "governed_persistence_envelope"


def _unwrap_governed_payload(value: Any) -> Any:
    """
    Read-side compatibility for Northstar 6A governed persistence.

    Writers may persist artifacts as:

        {
          "artifact_type": "governed_persistence_envelope",
          "payload": ...
        }

    State readers must evaluate the payload, not the envelope shell.
    """
    if (
        isinstance(value, dict)
        and value.get("artifact_type") == GOVERNED_PERSISTENCE_ENVELOPE
        and "payload" in value
    ):
        return value.get("payload")

    return value


def _load_json_any(path: Path) -> Any:
    if not path.exists():
        return {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

    return _unwrap_governed_payload(payload)


def _load_json_dict(path: Path) -> Dict[str, Any]:
    payload = _load_json_any(path)
    return dict(payload) if isinstance(payload, dict) else {}


def _load_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    records: List[Dict[str, Any]] = []

    for line in path.read_text(encoding="utf-8").splitlines():
        clean = line.strip()
        if not clean:
            continue

        try:
            payload = json.loads(clean)
        except json.JSONDecodeError:
            continue

        payload = _unwrap_governed_payload(payload)

        if isinstance(payload, dict):
            records.append(dict(payload))

    return records


def _normalize_phase_instances(payload: Any) -> List[Dict[str, Any]]:
    payload = _unwrap_governed_payload(payload)

    if isinstance(payload, list):
        return [dict(item) for item in payload if isinstance(item, dict)]

    if isinstance(payload, dict):
        phase_instances = _unwrap_governed_payload(payload.get("phase_instances", []))
        if isinstance(phase_instances, list):
            return [dict(item) for item in phase_instances if isinstance(item, dict)]

    return []


def read_contractor_project_state(project_id: str) -> Dict[str, Any]:
    project_root = resolve_contractor_project_root(project_id)
    workflow_root = project_root / "workflow"

    phase_instances_payload = _load_json_any(workflow_root / "phase_instances.json")

    return {
        "status": "ok" if project_root.exists() else "missing",
        "project_id": str(project_id or "").strip(),
        "project_root": str(project_root),
        "project_exists": project_root.exists(),
        "project_profile": _load_json_dict(project_root / "project_profile.json"),
        "baseline_lock": _load_json_dict(project_root / "baseline_lock.json"),
        "workflow_state": _load_json_dict(workflow_root / "workflow_state.json"),
        "phase_instances": _normalize_phase_instances(phase_instances_payload),
        "checklists": _load_json_dict(workflow_root / "checklists.json"),
        "client_signoff_status_records": _load_jsonl(
            workflow_root / "client_signoff_status.jsonl"
        ),
        "client_signoff_event_records": _load_jsonl(
            workflow_root / "client_signoff_history.jsonl"
        ),
    }


def find_phase_instance(
    *,
    project_state: Dict[str, Any],
    phase_id: str,
) -> Dict[str, Any]:
    clean_phase_id = str(phase_id or "").strip()
    phase_instances = project_state.get("phase_instances", [])

    if not isinstance(phase_instances, list):
        return {}

    for phase in phase_instances:
        if not isinstance(phase, dict):
            continue
        if str(phase.get("phase_id", "")).strip() == clean_phase_id:
            return dict(phase)

    return {}


def get_latest_signoff_status(
    *,
    project_state: Dict[str, Any],
    phase_id: str,
) -> Dict[str, Any]:
    clean_phase_id = str(phase_id or "").strip()
    records = project_state.get("client_signoff_status_records", [])

    if not isinstance(records, list):
        return {}

    matched = [
        dict(record)
        for record in records
        if isinstance(record, dict)
        and str(record.get("phase_id", "")).strip() == clean_phase_id
    ]

    return matched[-1] if matched else {}