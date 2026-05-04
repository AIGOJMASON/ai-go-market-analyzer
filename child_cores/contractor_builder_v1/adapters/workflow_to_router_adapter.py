"""
Workflow to router adapter for contractor_builder_v1.

This adapter translates workflow phase instances into schedule-block-style inputs
for the router branch. It does not create routing decisions or mutate workflow.
"""

from __future__ import annotations

from typing import Any, Dict, List


def build_router_blocks_from_phase_instances(
    *,
    project_id: str,
    phase_instances: List[Dict[str, Any]],
    default_resource_type: str = "phase_window",
) -> List[Dict[str, Any]]:
    """
    Translate workflow phase instances into thin router block inputs.
    """
    blocks: List[Dict[str, Any]] = []

    for instance in phase_instances:
        phase_id = str(instance.get("phase_id", "")).strip()
        if not phase_id:
            continue

        block = {
            "block_id": f"block-{project_id}-{phase_id}",
            "project_id": project_id,
            "phase_id": phase_id,
            "block_type": "Crew_Assignment",
            "start_date": instance.get("planned_start_date", "") or "",
            "end_date": instance.get("planned_end_date", "") or "",
            "resource_name": instance.get("phase_name", "") or phase_id,
            "resource_type": default_resource_type,
            "dependency_phase_ids": list(instance.get("dependencies", [])),
            "notes": "Derived from workflow phase instance by thin adapter.",
        }
        blocks.append(block)

    return blocks