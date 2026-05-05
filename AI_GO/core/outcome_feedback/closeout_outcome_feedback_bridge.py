from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from AI_GO.core.outcome_feedback.outcome_cycle_runner import (
    safely_run_outcome_cycle,
)


BRIDGE_VERSION = "northstar_closeout_bridge_v1"


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


def extract_closeout_outcome(
    *,
    closeout_payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Extract normalized outcome signals from closeout payload.

    This is intentionally minimal and non-opinionated.
    """
    payload = closeout_payload or {}

    return {
        "status": payload.get("status"),
        "project_id": payload.get("project_id"),
        "phase_id": payload.get("phase_id"),
        "signoff_status": payload.get("signoff_status"),
        "deliverables": payload.get("deliverables", []),
        "artifacts": payload.get("artifacts", []),
        "metadata": payload.get("metadata", {}),
    }


def run_closeout_outcome_bridge(
    *,
    closeout_payload: Dict[str, Any],
    source: str = "phase_closeout",
) -> Dict[str, Any]:
    """
    Bridge from closeout → outcome system.

    Northstar rules:
    - No mutation of workflow or project state
    - No authority escalation
    - Only translation + recording
    """

    normalized = extract_closeout_outcome(
        closeout_payload=closeout_payload,
    )

    project_id = _safe_str(normalized.get("project_id"))
    phase_id = _safe_str(normalized.get("phase_id"))

    if not project_id:
        raise ValueError("project_id is required in closeout payload")

    cycle_id = f"closeout-{phase_id or 'unknown'}"

    outcome_result = safely_run_outcome_cycle(
        project_id=project_id,
        cycle_id=cycle_id,
        inputs=normalized,
        outcomes=normalized,
        source=_safe_str(source),
    )

    return {
        "status": "ok",
        "artifact_type": "closeout_outcome_bridge",
        "artifact_version": BRIDGE_VERSION,
        "processed_at": _utc_now_iso(),
        "project_id": project_id,
        "phase_id": phase_id,
        "classification": _classification_block(),
        "authority": _authority_block(),
        "outcome_record": outcome_result,
        "sealed": True,
    }