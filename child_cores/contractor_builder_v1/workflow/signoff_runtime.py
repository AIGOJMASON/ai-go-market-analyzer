
"""
Workflow signoff runtime for contractor_builder_v1.

This module records append-only workflow/client signoff records.

Northstar Stage 6A rule:
No direct .write, .write_text, .write_bytes, or json.dump calls are permitted.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, Optional

from AI_GO.core.governance.governed_persistence import governed_append_jsonl
from AI_GO.core.state_runtime.state_paths import contractor_projects_root


STATE_ROOT = contractor_projects_root()


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def get_signoff_log_path(project_id: str) -> Path:
    return STATE_ROOT / _safe_str(project_id) / "workflow" / "signoff_status.jsonl"


def get_client_signoffs_path(project_id: str) -> Path:
    """
    Backward-compatible public contract expected by workflow package imports.
    """
    return STATE_ROOT / _safe_str(project_id) / "workflow" / "client_signoffs.jsonl"


def _classification_block(
    *,
    persistence_type: str = "contractor_workflow_signoff_record",
    mutation_class: str = "contractor_workflow_signoff_persistence",
) -> Dict[str, Any]:
    return {
        "persistence_type": persistence_type,
        "mutation_class": mutation_class,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "workflow_mutation_allowed": True,
        "state_mutation_allowed": True,
        "append_only": True,
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
        "layer": "workflow.signoff_runtime",
        "project_id": _safe_str(project_id),
        "phase_id": _safe_str(phase_id),
    }


def build_signoff_record(
    *,
    project_id: str,
    phase_id: str,
    status: str,
    actor: str = "signoff_runtime",
    notes: str = "",
    artifact_id: str = "",
) -> Dict[str, Any]:
    clean_project_id = _safe_str(project_id)
    clean_phase_id = _safe_str(phase_id)

    if not clean_project_id:
        raise ValueError("project_id is required")
    if not clean_phase_id:
        raise ValueError("phase_id is required")

    return {
        "artifact_type": "contractor_workflow_signoff_record",
        "artifact_version": "northstar_workflow_signoff_v1",
        "project_id": clean_project_id,
        "phase_id": clean_phase_id,
        "status": _safe_str(status),
        "actor": _safe_str(actor) or "signoff_runtime",
        "notes": notes,
        "artifact_id": _safe_str(artifact_id),
        "recorded_at": _utc_now_iso(),
        "classification": _classification_block(),
        "authority_metadata": _authority_metadata(
            operation="build_signoff_record",
            project_id=clean_project_id,
            phase_id=clean_phase_id,
        ),
        "sealed": True,
    }


def append_signoff_record(record: Dict[str, Any]) -> Path:
    if not isinstance(record, dict):
        raise ValueError("record must be a dict")

    project_id = _safe_str(record.get("project_id"))
    phase_id = _safe_str(record.get("phase_id"))

    if not project_id:
        raise ValueError("project_id is required")
    if not phase_id:
        raise ValueError("phase_id is required")

    payload = dict(record)
    payload["classification"] = _classification_block()
    payload["authority_metadata"] = _authority_metadata(
        operation="append_signoff_record",
        project_id=project_id,
        phase_id=phase_id,
    )
    payload["sealed"] = True

    path = get_signoff_log_path(project_id)

    governed_append_jsonl(
        path=path,
        payload=payload,
        mutation_class="contractor_workflow_signoff_persistence",
        persistence_type="contractor_workflow_signoff_record",
        authority_metadata=payload["authority_metadata"],
    )

    return path


def append_client_signoff_record(
    *,
    project_id: str,
    phase_id: str,
    client_name: str = "",
    result: str = "",
    checklist_completed: list[str] | None = None,
    notes: str = "",
    actor: str = "signoff_runtime",
    artifact_id: str = "",
    status: str = "",
) -> Dict[str, Any]:
    """
    Backward-compatible public contract expected by workflow package imports.

    Records a client signoff event in the client_signoffs.jsonl log.
    """
    clean_project_id = _safe_str(project_id)
    clean_phase_id = _safe_str(phase_id)
    clean_status = _safe_str(status) or _safe_str(result) or "recorded"

    if not clean_project_id:
        raise ValueError("project_id is required")
    if not clean_phase_id:
        raise ValueError("phase_id is required")

    payload: Dict[str, Any] = {
        "artifact_type": "contractor_client_signoff_record",
        "artifact_version": "northstar_client_signoff_v1",
        "project_id": clean_project_id,
        "phase_id": clean_phase_id,
        "client_name": _safe_str(client_name),
        "result": _safe_str(result) or clean_status,
        "status": clean_status,
        "checklist_completed": list(checklist_completed or []),
        "notes": notes,
        "actor": _safe_str(actor) or "signoff_runtime",
        "artifact_id": _safe_str(artifact_id),
        "recorded_at": _utc_now_iso(),
        "classification": _classification_block(
            persistence_type="contractor_client_signoff_record",
            mutation_class="contractor_client_signoff_persistence",
        ),
        "authority_metadata": _authority_metadata(
            operation="append_client_signoff_record",
            project_id=clean_project_id,
            phase_id=clean_phase_id,
        ),
        "sealed": True,
    }

    governed_append_jsonl(
        path=get_client_signoffs_path(clean_project_id),
        payload=payload,
        mutation_class="contractor_client_signoff_persistence",
        persistence_type="contractor_client_signoff_record",
        authority_metadata=payload["authority_metadata"],
    )

    return payload


def get_latest_signoff_record(
    *,
    project_id: str,
    phase_id: str,
) -> Optional[Dict[str, Any]]:
    path = get_signoff_log_path(project_id)
    if not path.exists():
        return None

    latest: Optional[Dict[str, Any]] = None

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return None

    for line in lines:
        clean = line.strip()
        if not clean:
            continue
        try:
            record = json.loads(clean)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict) and _safe_str(record.get("phase_id")) == _safe_str(phase_id):
            latest = record

    return latest