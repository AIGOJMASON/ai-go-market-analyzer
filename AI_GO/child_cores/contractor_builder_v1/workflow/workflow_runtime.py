"""
Workflow runtime for contractor_builder_v1.

This module initializes workflow state for a project and persists phase instance data.
It preserves separation between:
- workflow state creation
- template expansion
- drift detection
- signoff event recording
- checklist persistence
- automatic phase progression helpers

Northstar Stage 6A rule:
All runtime persistence must go through governed_persistence.
No direct json.dump, .write, .write_text, or .write_bytes calls.

Path anchoring rule:
All project workflow paths must resolve through AI_GO.core.state_runtime.state_paths.
No relative state roots are allowed.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List

from AI_GO.core.governance.governed_persistence import (
    governed_append_jsonl,
    governed_write_json,
)
from AI_GO.core.state_runtime.state_paths import contractor_projects_root

from ..governance.integrity import compute_hash_for_mapping
from .phase_instance_schema import validate_phase_instance
from .workflow_schema import WORKFLOW_SCHEMA_VERSION


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "y", "required"}:
            return True
        if lowered in {"0", "false", "no", "n", "optional"}:
            return False
    return bool(value)


def _model_to_dict(value: Any) -> Dict[str, Any]:
    """
    Convert dict-like or Pydantic objects into plain JSON-ready dictionaries.
    """
    if isinstance(value, dict):
        return dict(value)

    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        dumped = model_dump(mode="json")
        return dict(dumped) if isinstance(dumped, dict) else {}

    legacy_dict = getattr(value, "dict", None)
    if callable(legacy_dict):
        dumped = legacy_dict()
        return dict(dumped) if isinstance(dumped, dict) else {}

    return {}


def _normalize_status(value: Any) -> str:
    raw = _safe_str(value).lower()
    if raw in {"complete", "completed", "done", "closed"}:
        return "complete"
    if raw in {"not_started", "not started", "pending", "open", ""}:
        return "not_started"
    return raw


def _normalize_checklist_item(
    item: Any,
    *,
    project_id: str,
    phase_id: str,
    index: int,
) -> Dict[str, Any]:
    source = _model_to_dict(item)
    if not source:
        return {}

    clean_phase_id = _safe_str(source.get("phase_id")) or phase_id
    clean_item_id = _safe_str(source.get("item_id")) or f"item-{index + 1}"
    clean_label = _safe_str(source.get("label")) or clean_item_id

    normalized: Dict[str, Any] = {
        "item_id": clean_item_id,
        "phase_id": clean_phase_id,
        "label": clean_label,
        "required": _safe_bool(source.get("required", True), default=True),
        "status": _normalize_status(source.get("status")),
        "completed_by": source.get("completed_by"),
        "completed_at": source.get("completed_at"),
        "notes": source.get("notes"),
    }

    # Preserve any extra bounded fields without letting them override canon keys.
    for key, value in source.items():
        normalized.setdefault(key, value)

    normalized["project_id"] = _safe_str(source.get("project_id")) or project_id
    normalized["phase_id"] = clean_phase_id
    normalized["item_id"] = clean_item_id
    normalized["label"] = clean_label
    normalized["required"] = _safe_bool(source.get("required", True), default=True)
    normalized["status"] = _normalize_status(source.get("status"))

    return normalized


def _normalize_checklist_items(
    items: Any,
    *,
    project_id: str,
    phase_id: str,
) -> List[Dict[str, Any]]:
    if not isinstance(items, list):
        return []

    normalized: List[Dict[str, Any]] = []
    for index, item in enumerate(items):
        record = _normalize_checklist_item(
            item,
            project_id=project_id,
            phase_id=phase_id,
            index=index,
        )
        if record:
            normalized.append(record)

    return normalized


def get_project_workflow_root(project_id: str) -> Path:
    clean_project_id = _safe_str(project_id)
    if not clean_project_id:
        raise ValueError("project_id is required")
    return contractor_projects_root() / clean_project_id / "workflow"


def get_phase_instances_path(project_id: str) -> Path:
    return get_project_workflow_root(project_id) / "phase_instances.json"


def get_phase_history_path(project_id: str) -> Path:
    return get_project_workflow_root(project_id) / "phase_history.jsonl"


def get_workflow_state_path(project_id: str) -> Path:
    return get_project_workflow_root(project_id) / "workflow_state.json"


def get_checklists_path(project_id: str) -> Path:
    return get_project_workflow_root(project_id) / "checklists.json"


def get_checklist_path(project_id: str, phase_id: str) -> Path:
    return get_project_workflow_root(project_id) / "checklists" / f"{_safe_str(phase_id)}.json"


def _classification_block(persistence_type: str) -> Dict[str, Any]:
    return {
        "persistence_type": persistence_type,
        "mutation_class": "contractor_workflow_persistence",
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "workflow_mutation_allowed": True,
        "state_mutation_allowed": True,
        "project_truth_mutation_allowed": False,
        "advisory_only": False,
    }


def _authority_metadata(
    *,
    operation: str,
    project_id: str,
    phase_id: str = "",
) -> Dict[str, Any]:
    return {
        "authority_id": "northstar_stage_6a",
        "operation": operation,
        "child_core_id": "contractor_builder_v1",
        "layer": "workflow.workflow_runtime",
        "project_id": _safe_str(project_id),
        "phase_id": _safe_str(phase_id),
    }


def _validate_phase_instances(phase_instances: List[Dict[str, Any]]) -> None:
    for instance in phase_instances:
        if not isinstance(instance, dict):
            raise ValueError("Invalid phase instance: instance must be a dict")
        errors = validate_phase_instance(instance)
        if errors:
            raise ValueError("Invalid phase instance: " + "; ".join(errors))


def _unwrap_governed_payload(payload: Any) -> Any:
    """
    governed_write_json should persist the supplied payload, but older Stage 6A
    variants may wrap it. Readers accept both raw payloads and common envelopes.
    """
    if not isinstance(payload, dict):
        return payload

    for key in ("payload", "data", "artifact", "record", "content"):
        nested = payload.get(key)
        if isinstance(nested, (dict, list)):
            if isinstance(nested, dict) and nested is payload:
                continue
            return _unwrap_governed_payload(nested)

    return payload


def _load_json_mapping(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    payload = _unwrap_governed_payload(payload)
    return payload if isinstance(payload, dict) else {}


def _load_json_list(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []

    payload = _unwrap_governed_payload(payload)

    if isinstance(payload, list):
        return [dict(item) for item in payload if isinstance(item, dict)]

    if isinstance(payload, dict):
        items = payload.get("items") or payload.get("phases") or payload.get("phase_instances")
        if isinstance(items, list):
            return [dict(item) for item in items if isinstance(item, dict)]

    return []


def _persist_workflow_json(
    *,
    path: Path,
    payload: Any,
    persistence_type: str,
    operation: str,
    project_id: str,
    phase_id: str = "",
) -> None:
    governed_write_json(
        path=path,
        payload=payload,
        mutation_class="contractor_workflow_persistence",
        persistence_type=persistence_type,
        authority_metadata=_authority_metadata(
            operation=operation,
            project_id=project_id,
            phase_id=phase_id,
        ),
    )


def build_workflow_state_record(
    *,
    project_id: str,
    phase_count: int = 0,
) -> Dict[str, Any]:
    clean_project_id = _safe_str(project_id)
    if not clean_project_id:
        raise ValueError("project_id is required")

    base_record: Dict[str, Any] = {
        "schema_version": WORKFLOW_SCHEMA_VERSION,
        "project_id": clean_project_id,
        "workflow_status": "initialized",
        "phase_count": int(phase_count or 0),
        "current_phase_id": "",
        "created_at": _utc_now_iso(),
        "updated_at": _utc_now_iso(),
        "notes": "",
    }

    workflow_hash = compute_hash_for_mapping(base_record)

    record = dict(base_record)
    record["integrity"] = {
        "entry_hash": workflow_hash,
        "linked_receipts": [],
    }
    record["classification"] = _classification_block("contractor_workflow_state")
    record["authority_metadata"] = _authority_metadata(
        operation="build_workflow_state_record",
        project_id=clean_project_id,
    )
    record["sealed"] = True

    return record


def build_workflow_state(
    *,
    project_id: str,
    current_phase_id: str = "",
    workflow_status: str = "active",
    phase_count: int = 0,
    actor: str = "workflow_runtime",
) -> Dict[str, Any]:
    record = build_workflow_state_record(
        project_id=project_id,
        phase_count=phase_count,
    )
    record["workflow_status"] = _safe_str(workflow_status) or "active"
    record["current_phase_id"] = _safe_str(current_phase_id)
    record["actor"] = _safe_str(actor) or "workflow_runtime"
    record["updated_at"] = _utc_now_iso()

    record_for_hash = dict(record)
    record_for_hash["integrity"] = {
        "entry_hash": "",
        "linked_receipts": record.get("integrity", {}).get("linked_receipts", []),
    }
    record["integrity"] = {
        "entry_hash": compute_hash_for_mapping(record_for_hash),
        "linked_receipts": record.get("integrity", {}).get("linked_receipts", []),
    }
    record["classification"] = _classification_block("contractor_workflow_state")
    record["authority_metadata"] = _authority_metadata(
        operation="build_workflow_state",
        project_id=project_id,
        phase_id=current_phase_id,
    )
    record["sealed"] = True

    return record


def initialize_workflow_for_project(
    *,
    project_id: str,
    phase_instances: List[Dict[str, Any]],
    create_dirs: bool = True,
    overwrite: bool = False,
) -> Dict[str, Any]:
    clean_project_id = _safe_str(project_id)
    if not clean_project_id:
        raise ValueError("project_id is required")

    phase_instances = [dict(item) for item in phase_instances if isinstance(item, dict)]
    _validate_phase_instances(phase_instances)

    phase_instances_path = get_phase_instances_path(clean_project_id)
    workflow_state_path = get_workflow_state_path(clean_project_id)
    phase_history_path = get_phase_history_path(clean_project_id)
    checklists_path = get_checklists_path(clean_project_id)

    if phase_instances_path.exists() and not overwrite:
        raise FileExistsError(
            f"Workflow phase instances already exist and overwrite=False: {phase_instances_path}"
        )

    phase_count = len(phase_instances)

    workflow_state = build_workflow_state_record(
        project_id=clean_project_id,
        phase_count=phase_count,
    )

    if phase_instances:
        first_phase_id = _safe_str(phase_instances[0].get("phase_id"))
        workflow_state["current_phase_id"] = first_phase_id
        workflow_state["workflow_status"] = "active" if first_phase_id else "initialized"
        workflow_state["updated_at"] = _utc_now_iso()

    stamped_phase_instances = []
    for instance in phase_instances:
        phase_id = _safe_str(instance.get("phase_id"))
        stamped = dict(instance)
        stamped["classification"] = _classification_block("contractor_phase_instance")
        stamped["authority_metadata"] = _authority_metadata(
            operation="initialize_workflow_for_project",
            project_id=clean_project_id,
            phase_id=phase_id,
        )
        stamped["sealed"] = True
        stamped_phase_instances.append(stamped)

    _persist_workflow_json(
        path=phase_instances_path,
        payload=stamped_phase_instances,
        persistence_type="contractor_phase_instances",
        operation="initialize_phase_instances",
        project_id=clean_project_id,
    )

    _persist_workflow_json(
        path=workflow_state_path,
        payload=workflow_state,
        persistence_type="contractor_workflow_state",
        operation="initialize_workflow_state",
        project_id=clean_project_id,
        phase_id=_safe_str(workflow_state.get("current_phase_id")),
    )

    if not phase_history_path.exists():
        governed_append_jsonl(
            path=phase_history_path,
            payload={
                "artifact_type": "contractor_phase_history_event",
                "event_type": "workflow_initialized",
                "project_id": clean_project_id,
                "phase_id": _safe_str(workflow_state.get("current_phase_id")),
                "recorded_at": _utc_now_iso(),
                "classification": _classification_block("contractor_phase_history_event"),
                "authority_metadata": _authority_metadata(
                    operation="initialize_phase_history",
                    project_id=clean_project_id,
                    phase_id=_safe_str(workflow_state.get("current_phase_id")),
                ),
                "sealed": True,
            },
            mutation_class="contractor_workflow_persistence",
            persistence_type="contractor_phase_history_event",
            authority_metadata=_authority_metadata(
                operation="initialize_phase_history",
                project_id=clean_project_id,
                phase_id=_safe_str(workflow_state.get("current_phase_id")),
            ),
        )

    if not checklists_path.exists():
        _persist_workflow_json(
            path=checklists_path,
            payload={
                "artifact_type": "contractor_workflow_checklists",
                "project_id": clean_project_id,
                "checklists": {},
                "classification": _classification_block("contractor_workflow_checklists"),
                "authority_metadata": _authority_metadata(
                    operation="initialize_checklists",
                    project_id=clean_project_id,
                ),
                "sealed": True,
            },
            persistence_type="contractor_workflow_checklists",
            operation="initialize_checklists",
            project_id=clean_project_id,
        )

    return workflow_state


def upsert_phase_instances(
    *,
    project_id: str,
    phase_instances: List[Dict[str, Any]],
) -> Path:
    clean_project_id = _safe_str(project_id)
    if not clean_project_id:
        raise ValueError("project_id is required")

    phase_instances = [dict(item) for item in phase_instances if isinstance(item, dict)]
    _validate_phase_instances(phase_instances)

    stamped_phase_instances = []
    for instance in phase_instances:
        phase_id = _safe_str(instance.get("phase_id"))
        stamped = dict(instance)
        stamped["classification"] = _classification_block("contractor_phase_instance")
        stamped["authority_metadata"] = _authority_metadata(
            operation="upsert_phase_instances",
            project_id=clean_project_id,
            phase_id=phase_id,
        )
        stamped["sealed"] = True
        stamped_phase_instances.append(stamped)

    path = get_phase_instances_path(clean_project_id)

    _persist_workflow_json(
        path=path,
        payload=stamped_phase_instances,
        persistence_type="contractor_phase_instances",
        operation="upsert_phase_instances",
        project_id=clean_project_id,
    )

    return path


def write_phase_instances(
    *,
    project_id: str,
    phase_instances: List[Dict[str, Any]],
) -> Path:
    return upsert_phase_instances(
        project_id=project_id,
        phase_instances=phase_instances,
    )


def load_phase_instances(project_id: str) -> List[Dict[str, Any]]:
    return _load_json_list(get_phase_instances_path(project_id))


def load_workflow_state(project_id: str) -> Dict[str, Any]:
    return _load_json_mapping(get_workflow_state_path(project_id))


def persist_workflow_state(
    *,
    project_id: str,
    workflow_state: Dict[str, Any],
) -> Path:
    clean_project_id = _safe_str(project_id)
    if not clean_project_id:
        raise ValueError("project_id is required")

    payload = dict(workflow_state)
    payload["project_id"] = _safe_str(payload.get("project_id")) or clean_project_id
    payload["updated_at"] = _utc_now_iso()
    payload["classification"] = _classification_block("contractor_workflow_state")
    payload["authority_metadata"] = _authority_metadata(
        operation="persist_workflow_state",
        project_id=clean_project_id,
        phase_id=_safe_str(payload.get("current_phase_id")),
    )
    payload["sealed"] = True

    path = get_workflow_state_path(clean_project_id)

    _persist_workflow_json(
        path=path,
        payload=payload,
        persistence_type="contractor_workflow_state",
        operation="persist_workflow_state",
        project_id=clean_project_id,
        phase_id=_safe_str(payload.get("current_phase_id")),
    )

    return path


def write_workflow_state(state: Dict[str, Any]) -> Path:
    if not isinstance(state, dict):
        raise ValueError("state must be a dict")

    project_id = _safe_str(state.get("project_id"))
    if not project_id:
        raise ValueError("project_id is required")

    return persist_workflow_state(
        project_id=project_id,
        workflow_state=state,
    )


def _extract_checklists_mapping(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = _unwrap_governed_payload(payload)
    if not isinstance(payload, dict):
        return {}

    checklists = payload.get("checklists")
    if isinstance(checklists, dict):
        return dict(checklists)

    legacy: Dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, list):
            legacy[key] = value
    return legacy


def load_checklist(
    *,
    project_id: str,
    phase_id: str,
) -> List[Dict[str, Any]]:
    clean_project_id = _safe_str(project_id)
    clean_phase_id = _safe_str(phase_id)
    if not clean_project_id or not clean_phase_id:
        return []

    path = get_checklists_path(clean_project_id)

    if path.exists():
        payload = _load_json_mapping(path)
        checklists = _extract_checklists_mapping(payload)
        phase_items = checklists.get(clean_phase_id, [])

        if isinstance(phase_items, dict):
            phase_items = phase_items.get("items", [])

        if not isinstance(phase_items, list):
            raise ValueError(
                f"Invalid checklist items shape for phase_id={clean_phase_id} in {path}: expected list"
            )

        return _normalize_checklist_items(
            phase_items,
            project_id=clean_project_id,
            phase_id=clean_phase_id,
        )

    per_phase_path = get_checklist_path(clean_project_id, clean_phase_id)
    if not per_phase_path.exists():
        return []

    payload = _load_json_mapping(per_phase_path)
    items = payload.get("items", [])
    return _normalize_checklist_items(
        items,
        project_id=clean_project_id,
        phase_id=clean_phase_id,
    )


def upsert_checklist(
    *,
    project_id: str,
    phase_id: str,
    items: List[Dict[str, Any]],
) -> Path:
    clean_project_id = _safe_str(project_id)
    clean_phase_id = _safe_str(phase_id)

    if not clean_project_id:
        raise ValueError("project_id is required")
    if not clean_phase_id:
        raise ValueError("phase_id is required")

    path = get_checklists_path(clean_project_id)
    existing = _load_json_mapping(path) if path.exists() else {}
    checklists = _extract_checklists_mapping(existing)

    normalized_items = _normalize_checklist_items(
        items,
        project_id=clean_project_id,
        phase_id=clean_phase_id,
    )

    checklists[clean_phase_id] = normalized_items

    payload = {
        "artifact_type": "contractor_workflow_checklists",
        "project_id": clean_project_id,
        "checklists": checklists,
        "updated_at": _utc_now_iso(),
        "classification": _classification_block("contractor_workflow_checklists"),
        "authority_metadata": _authority_metadata(
            operation="upsert_checklist",
            project_id=clean_project_id,
            phase_id=clean_phase_id,
        ),
        "sealed": True,
    }

    _persist_workflow_json(
        path=path,
        payload=payload,
        persistence_type="contractor_workflow_checklists",
        operation="upsert_checklist",
        project_id=clean_project_id,
        phase_id=clean_phase_id,
    )

    return path


def write_checklist(
    *,
    project_id: str,
    phase_id: str,
    checklist_items: List[Dict[str, Any]],
) -> Path:
    return upsert_checklist(
        project_id=project_id,
        phase_id=phase_id,
        items=checklist_items,
    )


def append_phase_history(
    *,
    project_id: str,
    event: Dict[str, Any],
) -> Path:
    clean_project_id = _safe_str(project_id)
    if not clean_project_id:
        raise ValueError("project_id is required")

    payload_event = dict(event)
    payload_event.setdefault("project_id", clean_project_id)
    payload_event.setdefault("recorded_at", _utc_now_iso())
    payload_event["classification"] = _classification_block("contractor_phase_history_event")
    payload_event["authority_metadata"] = _authority_metadata(
        operation="append_phase_history",
        project_id=clean_project_id,
        phase_id=_safe_str(payload_event.get("phase_id")),
    )
    payload_event["sealed"] = True

    path = get_phase_history_path(clean_project_id)

    governed_append_jsonl(
        path=path,
        payload=payload_event,
        mutation_class="contractor_workflow_persistence",
        persistence_type="contractor_phase_history_event",
        authority_metadata=payload_event["authority_metadata"],
    )

    return path


def reconcile_workflow_state(
    *,
    project_id: str,
    actor: str = "workflow_runtime",
) -> Dict[str, Any]:
    workflow_state = load_workflow_state(project_id)
    phase_instances = load_phase_instances(project_id)

    current_phase_id = _safe_str(workflow_state.get("current_phase_id"))
    current_phase: Dict[str, Any] = {}

    for phase in phase_instances:
        if _safe_str(phase.get("phase_id")) == current_phase_id:
            current_phase = phase
            break

    checklist_items = load_checklist(
        project_id=project_id,
        phase_id=current_phase_id,
    ) if current_phase_id else []

    required_items = [
        item for item in checklist_items
        if _safe_bool(item.get("required", True), default=True) is True
    ]

    completed_required = [
        item
        for item in required_items
        if _normalize_status(item.get("status")) == "complete"
    ]

    required_item_count = len(required_items)
    completed_required_count = len(completed_required)

    checklist_summary = {
        "project_id": project_id,
        "phase_id": current_phase_id,
        "required_item_count": required_item_count,
        "required_count": required_item_count,
        "completed_required_count": completed_required_count,
        "ready_for_signoff": bool(
            required_item_count > 0
            and required_item_count == completed_required_count
        ),
        "actor": actor,
        "checked_at": _utc_now_iso(),
    }

    latest_signoff_status: Dict[str, Any] = {}
    try:
        from .client_signoff_status_runtime import get_latest_client_signoff_status

        latest = get_latest_client_signoff_status(
            project_id=project_id,
            phase_id=current_phase_id,
        )
        latest_signoff_status = dict(latest) if isinstance(latest, dict) else {}
    except Exception:
        latest_signoff_status = {}

    return {
        "status": "reconciled",
        "project_id": project_id,
        "workflow_state": workflow_state,
        "phase_instances": phase_instances,
        "current_phase": current_phase,
        "current_phase_id": current_phase_id,
        "checklist_summary": checklist_summary,
        "latest_signoff_status": latest_signoff_status,
        "classification": _classification_block("contractor_workflow_reconciliation"),
        "authority_metadata": _authority_metadata(
            operation="reconcile_workflow_state",
            project_id=project_id,
            phase_id=current_phase_id,
        ),
        "sealed": True,
    }


def advance_phase_if_ready(
    *,
    project_id: str,
    current_phase_id: str,
    signoff_status: str,
) -> Dict[str, Any]:
    if signoff_status != "signed":
        return {"advanced": False, "reason": "signoff_not_signed"}

    phases = load_phase_instances(project_id)
    phase_ids = [_safe_str(item.get("phase_id")) for item in phases]

    if current_phase_id not in phase_ids:
        return {"advanced": False, "reason": "phase_not_found"}

    idx = phase_ids.index(current_phase_id)

    if idx + 1 >= len(phase_ids):
        return {"advanced": False, "reason": "no_next_phase"}

    next_phase = phase_ids[idx + 1]

    state = load_workflow_state(project_id)
    state["project_id"] = project_id
    state["current_phase_id"] = next_phase
    state["workflow_status"] = _safe_str(state.get("workflow_status")) or "active"
    state["updated_at"] = _utc_now_iso()
    state["classification"] = _classification_block("contractor_workflow_state")
    state["authority_metadata"] = _authority_metadata(
        operation="advance_phase_if_ready",
        project_id=project_id,
        phase_id=next_phase,
    )
    state["sealed"] = True

    write_workflow_state(state)

    append_phase_history(
        project_id=project_id,
        event={
            "event_type": "phase_advanced",
            "from_phase_id": current_phase_id,
            "to_phase_id": next_phase,
            "phase_id": next_phase,
        },
    )

    return {"advanced": True, "next_phase_id": next_phase}
