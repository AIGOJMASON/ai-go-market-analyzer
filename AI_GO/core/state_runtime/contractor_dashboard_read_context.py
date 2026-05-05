from __future__ import annotations

from typing import Any, Dict

from AI_GO.child_cores.contractor_builder_v1.workflow.workflow_runtime import (
    reconcile_workflow_state,
)


def build_dashboard_read_context(
    *,
    project_id: str,
    persist_packet: bool = False,
) -> Dict[str, Any]:
    """
    Build dashboard read context.

    NORTHSTAR RULE:
    - This function MUST NOT persist by default.
    - persist_packet flag is accepted for forward compatibility only.
    - Actual persistence must be handled by a separate governed layer.
    """

    # --- Core workflow snapshot ---
    reconciliation = reconcile_workflow_state(
        project_id=project_id,
        actor="dashboard_read_context",
    )

    workflow_state = reconciliation.get("workflow_state", {})
    phase_instances = reconciliation.get("phase_instances", [])
    current_phase_id = reconciliation.get("current_phase_id", "")

    # --- Build dashboard structure ---
    dashboard: Dict[str, Any] = {
        "project_id": project_id,
        "current_phase_id": current_phase_id,
        "workflow_state": workflow_state,
        "phase_instances": phase_instances,
        "artifact_paths": reconciliation.get("artifact_paths", {}),
        "receipt_paths": reconciliation.get("receipt_paths", []),
    }

    # --- NORTHSTAR ENFORCEMENT ---
    # No persistence occurs here.
    # persist_packet is intentionally ignored for now.
    # This prevents hidden mutation inside read flows.

    return dashboard