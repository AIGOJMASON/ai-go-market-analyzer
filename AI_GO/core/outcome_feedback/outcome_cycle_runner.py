from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


OUTCOME_CYCLE_VERSION = "northstar_outcome_v1"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _authority_block() -> Dict[str, Any]:
    return {
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
        "persistence_type": "outcome_feedback",
        "mutation_class": "outcome_persistence",
        "execution_allowed": False,
        "state_mutation_allowed": False,
        "workflow_mutation_allowed": False,
        "project_truth_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "advisory_only": True,
    }


def run_outcome_cycle(
    *,
    project_id: str,
    cycle_id: str,
    inputs: Dict[str, Any] | None = None,
    outcomes: Dict[str, Any] | None = None,
    source: str = "contractor_outcome_cycle",
) -> Dict[str, Any]:
    """
    Outcome cycle runner.

    Northstar rules:
    - Records outcome signals only
    - Does not mutate system state
    - Does not influence execution directly
    """

    clean_project_id = _safe_str(project_id)
    clean_cycle_id = _safe_str(cycle_id)
    clean_source = _safe_str(source)

    if not clean_project_id:
        raise ValueError("project_id is required")

    if not clean_cycle_id:
        raise ValueError("cycle_id is required")

    result = {
        "status": "recorded",
        "artifact_type": "outcome_cycle_record",
        "artifact_version": OUTCOME_CYCLE_VERSION,
        "recorded_at": _utc_now_iso(),
        "project_id": clean_project_id,
        "cycle_id": clean_cycle_id,
        "source": clean_source,
        "inputs": inputs or {},
        "outcomes": outcomes or {},
        "classification": _classification_block(),
        "authority": _authority_block(),
        "sealed": True,
    }

    return result


def safely_run_outcome_cycle(
    *,
    project_id: str,
    cycle_id: str,
    inputs: Dict[str, Any] | None = None,
    outcomes: Dict[str, Any] | None = None,
    source: str = "contractor_outcome_cycle",
) -> Dict[str, Any]:
    try:
        return run_outcome_cycle(
            project_id=project_id,
            cycle_id=cycle_id,
            inputs=inputs,
            outcomes=outcomes,
            source=source,
        )
    except Exception as exc:
        return {
            "status": "failed",
            "artifact_type": "outcome_cycle_record",
            "artifact_version": OUTCOME_CYCLE_VERSION,
            "recorded_at": _utc_now_iso(),
            "project_id": _safe_str(project_id),
            "cycle_id": _safe_str(cycle_id),
            "source": _safe_str(source),
            "classification": _classification_block(),
            "authority": _authority_block(),
            "error": f"{type(exc).__name__}: {exc}",
            "sealed": True,
        }