# AI_GO/core/paths/path_resolver.py

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


class PathResolverError(ValueError):
    pass


def _discover_project_root() -> Path:
    """
    Resolve the AI_GO project root.

    Priority:
    1. AI_GO_PROJECT_ROOT environment variable
    2. Walk upward from this file until app.py is found
    """
    env_root = os.getenv("AI_GO_PROJECT_ROOT", "").strip()
    if env_root:
        root = Path(env_root).expanduser().resolve()
        if not root.exists():
            raise PathResolverError(f"AI_GO_PROJECT_ROOT does not exist: {root}")
        return root

    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "app.py").exists():
            return parent

    raise PathResolverError("Unable to discover AI_GO project root.")


PROJECT_ROOT: Path = _discover_project_root()
STATE_ROOT: Path = PROJECT_ROOT / "state"
RECEIPTS_ROOT: Path = PROJECT_ROOT / "receipts"

CONTRACTOR_STATE_ROOT: Path = STATE_ROOT / "contractor_builder_v1"
CONTRACTOR_PROJECTS_ROOT: Path = CONTRACTOR_STATE_ROOT / "projects" / "by_project"

CONTRACTOR_RECEIPTS_ROOT: Path = RECEIPTS_ROOT / "contractor_builder_v1"
MARKET_RECEIPTS_ROOT: Path = RECEIPTS_ROOT / "market_analyzer_v1"


def ensure_dir(path: Path) -> Path:
    resolved = path.resolve()
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def ensure_parent(path: Path) -> Path:
    resolved = path.resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def resolve_under_root(*parts: str) -> Path:
    return (PROJECT_ROOT.joinpath(*parts)).resolve()


def get_project_root() -> Path:
    return PROJECT_ROOT


def get_state_root() -> Path:
    return ensure_dir(STATE_ROOT)


def get_receipts_root() -> Path:
    return ensure_dir(RECEIPTS_ROOT)


def get_contractor_state_root() -> Path:
    return ensure_dir(CONTRACTOR_STATE_ROOT)


def get_contractor_projects_root() -> Path:
    return ensure_dir(CONTRACTOR_PROJECTS_ROOT)


def get_contractor_project_root(project_id: str) -> Path:
    clean_project_id = str(project_id or "").strip()
    if not clean_project_id:
        raise PathResolverError("project_id is required")
    return ensure_dir(CONTRACTOR_PROJECTS_ROOT / clean_project_id)


def get_contractor_project_workflow_root(project_id: str) -> Path:
    return ensure_dir(get_contractor_project_root(project_id) / "workflow")


def get_contractor_project_documents_root(project_id: str) -> Path:
    return ensure_dir(get_contractor_project_root(project_id) / "documents")


def get_contractor_phase_closeout_documents_root(project_id: str) -> Path:
    return ensure_dir(
        get_contractor_project_documents_root(project_id) / "phase_closeout_pdfs"
    )


def get_contractor_project_delivery_root(project_id: str) -> Path:
    return ensure_dir(get_contractor_project_root(project_id) / "delivery")


def get_contractor_project_receipts_root(
    project_id: str,
    module_name: Optional[str] = None,
) -> Path:
    root = get_contractor_project_root(project_id) / "receipts"
    if module_name:
        root = root / str(module_name).strip()
    return ensure_dir(root)


def get_contractor_receipts_root(module_name: Optional[str] = None) -> Path:
    root = CONTRACTOR_RECEIPTS_ROOT
    if module_name:
        root = root / str(module_name).strip()
    return ensure_dir(root)


def get_market_receipts_root(module_name: Optional[str] = None) -> Path:
    root = MARKET_RECEIPTS_ROOT
    if module_name:
        root = root / str(module_name).strip()
    return ensure_dir(root)


def get_project_profile_path(project_id: str) -> Path:
    return ensure_parent(get_contractor_project_root(project_id) / "project_profile.json")


def get_baseline_lock_path(project_id: str) -> Path:
    return ensure_parent(get_contractor_project_root(project_id) / "baseline_lock.json")


def get_workflow_state_path(project_id: str) -> Path:
    return ensure_parent(
        get_contractor_project_workflow_root(project_id) / "workflow_state.json"
    )


def get_phase_instances_path(project_id: str) -> Path:
    return ensure_parent(
        get_contractor_project_workflow_root(project_id) / "phase_instances.json"
    )


def get_phase_history_path(project_id: str) -> Path:
    return ensure_parent(
        get_contractor_project_workflow_root(project_id) / "phase_history.jsonl"
    )


def get_checklists_path(project_id: str) -> Path:
    return ensure_parent(
        get_contractor_project_workflow_root(project_id) / "checklists.json"
    )


def get_client_signoff_status_path(project_id: str) -> Path:
    return ensure_parent(
        get_contractor_project_workflow_root(project_id)
        / "client_signoff_status.jsonl"
    )


def get_client_signoff_history_path(project_id: str) -> Path:
    return ensure_parent(
        get_contractor_project_workflow_root(project_id) / "client_signoffs.jsonl"
    )