"""
Latest payload state for contractor_builder_v1.

This module persists operator visibility payloads only.

Northstar rule:
- Persistence = mutation.
- Visibility persistence is allowed only when explicitly requested by a caller.
- This module may write visibility snapshots.
- It must not mutate workflow truth, project truth, PM authority, watcher truth,
  state authority, execution authority, or cross-core authority.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict

from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.state_runtime.state_paths import contractor_projects_root, state_root


VISIBILITY_STATE_ROOT = state_root() / "contractor_builder_v1" / "visibility"
PROJECTS_ROOT = contractor_projects_root()


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _unwrap_governed_payload(payload: Any) -> Any:
    if isinstance(payload, dict) and payload.get("artifact_type") == "governed_persistence_envelope":
        return payload.get("payload", {})
    return payload


def get_latest_payload_path() -> Path:
    return VISIBILITY_STATE_ROOT / "latest_dashboard_payload.json"


def get_by_request_root() -> Path:
    return VISIBILITY_STATE_ROOT / "by_request"


def get_project_latest_payload_path(project_id: str) -> Path:
    return PROJECTS_ROOT / _clean_text(project_id) / "projection" / "latest_operator_payload.json"


def get_project_by_request_root(project_id: str) -> Path:
    return PROJECTS_ROOT / _clean_text(project_id) / "projection" / "by_request"


def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": "visibility_snapshot",
        "mutation_class": "visibility_persistence",
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "workflow_mutation_allowed": False,
        "project_truth_mutation_allowed": False,
        "recommendation_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "advisory_only": True,
    }


def _authority_metadata(
    *,
    operation: str,
    project_id: str,
    request_id: str,
    source: str,
) -> Dict[str, Any]:
    return {
        "authority_id": "northstar_stage_6b_import_repair",
        "operation": operation,
        "child_core_id": "contractor_builder_v1",
        "layer": "projection.latest_payload_state",
        "project_id": _clean_text(project_id),
        "request_id": _clean_text(request_id),
        "source": _clean_text(source),
        "can_execute": False,
        "can_mutate_workflow_truth": False,
        "can_mutate_project_truth": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
    }


def _build_visibility_envelope(
    *,
    payload: Dict[str, Any],
    request_id: str,
    project_id: str,
    source: str,
) -> Dict[str, Any]:
    return {
        "artifact_type": "contractor_visibility_payload",
        "artifact_version": "northstar_visibility_v2",
        "persisted_at": _utc_now_iso(),
        "source": _clean_text(source) or "unknown",
        "request_id": _clean_text(request_id),
        "project_id": _clean_text(project_id),
        "classification": _classification_block(),
        "payload": dict(payload),
        "sealed": True,
    }


def _persist_visibility(
    *,
    path: Path,
    payload: Dict[str, Any],
    operation: str,
    project_id: str,
    request_id: str,
    source: str,
) -> None:
    governed_write_json(
        path=path,
        payload=payload,
        mutation_class="visibility_persistence",
        persistence_type="visibility_snapshot",
        authority_metadata=_authority_metadata(
            operation=operation,
            project_id=project_id,
            request_id=request_id,
            source=source,
        ),
    )


def persist_latest_dashboard_payload(
    *,
    project_id: str,
    payload: Dict[str, Any],
    request_id: str = "",
    source: str = "latest_payload_state",
    persist_global: bool = True,
    persist_project: bool = True,
    persist_by_request: bool = True,
) -> Dict[str, str]:
    clean_project_id = _clean_text(project_id)
    if not clean_project_id:
        raise ValueError("project_id is required")

    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")

    clean_request_id = _clean_text(request_id) or _clean_text(payload.get("request_id"))
    clean_source = _clean_text(source) or "latest_payload_state"

    envelope = _build_visibility_envelope(
        payload=payload,
        request_id=clean_request_id,
        project_id=clean_project_id,
        source=clean_source,
    )

    written_paths: Dict[str, str] = {}

    if persist_global:
        latest_path = get_latest_payload_path()
        _persist_visibility(
            path=latest_path,
            payload=envelope,
            operation="persist_global_latest_dashboard_payload",
            project_id=clean_project_id,
            request_id=clean_request_id,
            source=clean_source,
        )
        written_paths["global_latest_path"] = str(latest_path)

    if persist_project:
        project_latest_path = get_project_latest_payload_path(clean_project_id)
        _persist_visibility(
            path=project_latest_path,
            payload=envelope,
            operation="persist_project_latest_dashboard_payload",
            project_id=clean_project_id,
            request_id=clean_request_id,
            source=clean_source,
        )
        written_paths["project_latest_path"] = str(project_latest_path)

    if persist_by_request and clean_request_id:
        global_request_path = get_by_request_root() / f"{clean_request_id}.json"
        project_request_path = get_project_by_request_root(clean_project_id) / f"{clean_request_id}.json"

        _persist_visibility(
            path=global_request_path,
            payload=envelope,
            operation="persist_global_by_request_dashboard_payload",
            project_id=clean_project_id,
            request_id=clean_request_id,
            source=clean_source,
        )
        _persist_visibility(
            path=project_request_path,
            payload=envelope,
            operation="persist_project_by_request_dashboard_payload",
            project_id=clean_project_id,
            request_id=clean_request_id,
            source=clean_source,
        )

        written_paths["global_request_path"] = str(global_request_path)
        written_paths["project_request_path"] = str(project_request_path)

    return written_paths


def persist_latest_operator_payload(
    *,
    payload: Dict[str, Any],
    request_id: str = "",
    project_id: str,
    persist_global: bool = True,
    persist_project: bool = True,
    persist_by_request: bool = True,
    source: str = "operator_projection",
) -> Dict[str, str]:
    return persist_latest_dashboard_payload(
        project_id=project_id,
        payload=payload,
        request_id=request_id,
        source=source,
        persist_global=persist_global,
        persist_project=persist_project,
        persist_by_request=persist_by_request,
    )


def read_latest_operator_payload(project_id: str = "") -> Dict[str, Any]:
    candidate_paths = []
    clean_project_id = _clean_text(project_id)

    if clean_project_id:
        candidate_paths.append(get_project_latest_payload_path(clean_project_id))

    candidate_paths.append(get_latest_payload_path())

    for path in candidate_paths:
        if not path.exists():
            continue

        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        unwrapped = _unwrap_governed_payload(parsed)
        if not isinstance(unwrapped, dict):
            continue

        envelope = _safe_dict(unwrapped)
        payload = _safe_dict(envelope.get("payload"))
        if payload:
            return payload

        return envelope

    return {}