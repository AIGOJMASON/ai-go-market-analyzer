from __future__ import annotations

from pathlib import Path


class PathDriftViolation(RuntimeError):
    """Raised when code attempts to resolve or use a non-canonical AI_GO path."""


def project_root() -> Path:
    """
    Return the canonical AI_GO project root.

    This file lives at:
        AI_GO/core/state_runtime/state_paths.py

    Therefore parents[2] is:
        AI_GO/
    """
    return Path(__file__).resolve().parents[2]


def state_root() -> Path:
    """
    Return the single canonical state root.

    No fallback roots are allowed. Runtime state must always resolve under:
        <PROJECT_ROOT>/state
    """
    return project_root() / "state"


def receipts_root() -> Path:
    """
    Return the single canonical receipts root.
    """
    return project_root() / "receipts"


def logs_root() -> Path:
    """
    Return the single canonical logs root.
    """
    return project_root() / "logs"


def _resolved(path: Path) -> Path:
    return path.expanduser().resolve()


def assert_under_project_root(path: Path) -> Path:
    """
    Ensure a path resolves under the canonical project root.

    This prevents:
        C:/Users/J/Desktop/state
        C:/Users/J/Desktop/receipts
        C:/Users/J/Desktop/logs
        C:/Users/J/Desktop/AI_GO/AI_GO/state
    """
    root = _resolved(project_root())
    candidate = _resolved(path)

    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise PathDriftViolation(
            f"path_drift_violation: path is outside canonical project root: {candidate}"
        ) from exc

    parts = tuple(part.lower() for part in candidate.parts)

    for index in range(len(parts) - 1):
        if parts[index] == "ai_go" and parts[index + 1] == "ai_go":
            raise PathDriftViolation(
                f"path_drift_violation: nested AI_GO root is forbidden: {candidate}"
            )

    return candidate


def assert_under_state_root(path: Path) -> Path:
    """
    Ensure a path resolves under the canonical state root.
    """
    root = _resolved(state_root())
    candidate = assert_under_project_root(path)

    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise PathDriftViolation(
            f"path_drift_violation: path is outside canonical state root: {candidate}"
        ) from exc

    return candidate


def contractor_projects_root() -> Path:
    """
    Return the only valid contractor project state root.
    """
    return state_root() / "contractor_builder_v1" / "projects" / "by_project"


def contractor_project_root(project_id: str) -> Path:
    """
    Return canonical contractor project root for a project_id.

    This function does not search fallback roots.
    Missing project folders are still returned canonically so creators can create
    them through governed persistence.
    """
    clean_project_id = str(project_id or "").strip()
    if not clean_project_id:
        raise ValueError("project_id is required")

    return assert_under_state_root(contractor_projects_root() / clean_project_id)


def resolve_contractor_project_root(project_id: str) -> Path:
    """
    Backward-compatible name for existing imports.

    Important:
    This no longer resolves legacy fallback locations. It always returns the
    canonical location under <PROJECT_ROOT>/state.
    """
    return contractor_project_root(project_id)