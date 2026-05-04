from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from AI_GO.core.awareness.cross_run_intelligence import (
    append_unified_awareness_history_record,
)


SYSTEM_BRAIN_PERSISTENCE_VERSION = "northstar_awareness_v1"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _authority_block() -> Dict[str, Any]:
    return {
        "visibility_artifact_only": True,
        "advisory_only": True,
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
    }


def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": "system_brain_cycle_snapshot",
        "mutation_class": "awareness_persistence",
        "execution_allowed": False,
        "state_mutation_allowed": False,
        "workflow_mutation_allowed": False,
        "project_truth_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "advisory_only": True,
    }


def _build_run_id(
    *,
    request_id: str,
    project_id: str = "",
    phase_id: str = "",
    source: str = "contractor_live_dashboard",
) -> str:
    run_id_parts = [
        "system-brain-cycle",
        _safe_str(source) or "unknown_source",
        _safe_str(request_id) or "unknown_request",
    ]

    if project_id:
        run_id_parts.append(_safe_str(project_id))

    if phase_id:
        run_id_parts.append(_safe_str(phase_id))

    run_id_parts.append(datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))

    return "-".join(part.replace(" ", "_") for part in run_id_parts if part)


def persist_system_brain_cycle_snapshot(
    *,
    request_id: str,
    project_id: str = "",
    phase_id: str = "",
    source: str = "contractor_live_dashboard",
    limit: int = 500,
) -> Dict[str, Any]:
    """
    Persist one System Brain awareness cycle.

    Northstar rule:
    - This is awareness persistence only.
    - It may append cross-run awareness history.
    - It may not mutate contractor workflow truth.
    - It may not alter watcher, execution gate, state authority, PM authority,
      signoff, decision, risk, or project state.
    """
    clean_request_id = _safe_str(request_id)
    clean_project_id = _safe_str(project_id)
    clean_phase_id = _safe_str(phase_id)
    clean_source = _safe_str(source) or "contractor_live_dashboard"

    if not clean_request_id:
        raise ValueError("request_id is required for system brain awareness persistence")

    run_id = _build_run_id(
        request_id=clean_request_id,
        project_id=clean_project_id,
        phase_id=clean_phase_id,
        source=clean_source,
    )

    write_result = append_unified_awareness_history_record(
        run_id=run_id,
        limit=limit,
    )

    return {
        "status": "persisted",
        "artifact_type": "system_brain_cycle_persistence",
        "artifact_version": SYSTEM_BRAIN_PERSISTENCE_VERSION,
        "persisted_at": _utc_now_iso(),
        "request_id": clean_request_id,
        "project_id": clean_project_id,
        "phase_id": clean_phase_id,
        "source": clean_source,
        "run_id": run_id,
        "classification": _classification_block(),
        "authority": _authority_block(),
        "history_write": write_result,
        "sealed": True,
    }


def safely_persist_system_brain_cycle_snapshot(
    *,
    request_id: str,
    project_id: str = "",
    phase_id: str = "",
    source: str = "contractor_live_dashboard",
    limit: int = 500,
) -> Dict[str, Any]:
    try:
        return persist_system_brain_cycle_snapshot(
            request_id=request_id,
            project_id=project_id,
            phase_id=phase_id,
            source=source,
            limit=limit,
        )
    except Exception as exc:
        return {
            "status": "failed",
            "artifact_type": "system_brain_cycle_persistence",
            "artifact_version": SYSTEM_BRAIN_PERSISTENCE_VERSION,
            "persisted_at": _utc_now_iso(),
            "request_id": _safe_str(request_id),
            "project_id": _safe_str(project_id),
            "phase_id": _safe_str(phase_id),
            "source": _safe_str(source),
            "classification": _classification_block(),
            "authority": _authority_block(),
            "error": f"{type(exc).__name__}: {exc}",
            "sealed": True,
        }