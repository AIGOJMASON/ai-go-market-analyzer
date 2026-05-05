from __future__ import annotations

from typing import Any, Dict

from AI_GO.core.state_runtime.state_reader import (
    find_phase_instance,
    get_latest_signoff_status,
    read_contractor_project_state,
)


def build_project_state_context(project_id: str) -> Dict[str, Any]:
    return read_contractor_project_state(project_id)


def build_phase_state_context(
    *,
    project_id: str,
    phase_id: str,
) -> Dict[str, Any]:
    project_state = read_contractor_project_state(project_id)

    return {
        "status": "ok" if project_state.get("project_exists") else "missing",
        "project_id": project_id,
        "phase_id": phase_id,
        "project_state": project_state,
        "workflow_state": project_state.get("workflow_state", {}),
        "phase_instance": find_phase_instance(
            project_state=project_state,
            phase_id=phase_id,
        ),
        "latest_signoff_status": get_latest_signoff_status(
            project_state=project_state,
            phase_id=phase_id,
        ),
    }