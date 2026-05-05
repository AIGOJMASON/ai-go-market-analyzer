"""
Client signoff status runtime for contractor_builder_v1.
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


def _status_log_path(project_id: str) -> Path:
    return STATE_ROOT / _safe_str(project_id) / "workflow" / "client_signoff_status.jsonl"


def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": "contractor_client_signoff_status_record",
        "mutation_class": "contractor_client_signoff_status_persistence",
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "workflow_mutation_allowed": True,
        "append_only": True,
        "advisory_only": False,
    }


def _authority_metadata(
    *,
    operation: str,
    project_id: str,
    phase_id: str,
) -> Dict[str, Any]:
    return {
        "authority_id": "northstar_stage_6a",
        "operation": operation,
        "child_core_id": "contractor_builder_v1",
        "layer": "workflow.client_signoff_status_runtime",
        "project_id": _safe_str(project_id),
        "phase_id": _safe_str(phase_id),
    }


def _prepare_status(signoff: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(signoff)
    payload["classification"] = _classification_block()
    payload["authority_metadata"] = _authority_metadata(
        operation="prepare_client_signoff_status",
        project_id=_safe_str(payload.get("project_id")),
        phase_id=_safe_str(payload.get("phase_id")),
    )
    payload["sealed"] = True
    return payload


def build_initial_signoff(
    project_id: str,
    phase_id: str,
    client_name: str,
    client_email: str,
) -> Dict[str, Any]:
    return {
        "project_id": _safe_str(project_id),
        "phase_id": _safe_str(phase_id),
        "status": "not_requested",
        "client_name": _safe_str(client_name),
        "client_email": _safe_str(client_email),
        "pdf_artifact_id": None,
        "sent_at": None,
        "opened_at": None,
        "signed_at": None,
        "declined_at": None,
        "recorded_at": _utc_now_iso(),
        "classification": _classification_block(),
        "authority_metadata": _authority_metadata(
            operation="build_initial_signoff",
            project_id=project_id,
            phase_id=phase_id,
        ),
        "sealed": True,
    }


def mark_sent(signoff: Dict[str, Any], artifact_id: str) -> Dict[str, Any]:
    updated = dict(signoff)
    updated["status"] = "sent"
    updated["pdf_artifact_id"] = artifact_id
    updated["sent_at"] = _utc_now_iso()
    updated["recorded_at"] = _utc_now_iso()
    return _prepare_status(updated)


def mark_signed(signoff: Dict[str, Any]) -> Dict[str, Any]:
    updated = dict(signoff)
    updated["status"] = "signed"
    updated["signed_at"] = _utc_now_iso()
    updated["recorded_at"] = _utc_now_iso()
    return _prepare_status(updated)


def mark_declined(signoff: Dict[str, Any]) -> Dict[str, Any]:
    updated = dict(signoff)
    updated["status"] = "declined"
    updated["declined_at"] = _utc_now_iso()
    updated["recorded_at"] = _utc_now_iso()
    return _prepare_status(updated)


def append_client_signoff_status(signoff: Dict[str, Any]) -> Path:
    if not isinstance(signoff, dict):
        raise ValueError("signoff must be a dict")

    project_id = _safe_str(signoff.get("project_id"))
    phase_id = _safe_str(signoff.get("phase_id"))

    if not project_id:
        raise ValueError("project_id is required")
    if not phase_id:
        raise ValueError("phase_id is required")

    path = _status_log_path(project_id)
    payload = _prepare_status(signoff)

    governed_append_jsonl(
        path=path,
        payload=payload,
        mutation_class="contractor_client_signoff_status_persistence",
        persistence_type="contractor_client_signoff_status_record",
        authority_metadata=_authority_metadata(
            operation="append_client_signoff_status",
            project_id=project_id,
            phase_id=phase_id,
        ),
    )

    return path


def get_latest_client_signoff_status(
    project_id: str,
    phase_id: str,
) -> Optional[Dict[str, Any]]:
    path = _status_log_path(project_id)
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