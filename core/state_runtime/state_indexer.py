from __future__ import annotations

from typing import Any, Dict, List

from AI_GO.core.state_runtime.state_paths import contractor_projects_root_candidates


def list_contractor_project_ids() -> List[str]:
    seen: set[str] = set()
    project_ids: List[str] = []

    for root in contractor_projects_root_candidates():
        if not root.exists():
            continue

        for path in root.iterdir():
            if not path.is_dir():
                continue

            project_id = path.name
            if project_id in seen:
                continue

            seen.add(project_id)
            project_ids.append(project_id)

    return sorted(project_ids)


def build_state_index() -> Dict[str, Any]:
    project_ids = list_contractor_project_ids()

    return {
        "status": "ok",
        "state_runtime": "v1.0",
        "contractor_builder_v1": {
            "project_count": len(project_ids),
            "project_ids": project_ids,
        },
    }