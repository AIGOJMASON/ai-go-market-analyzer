"""
Baseline lock runtime for contractor_builder_v1.

Creates and persists the initial project baseline lock record.

Northstar Stage 6A:
- NO raw writes
- governed persistence ONLY
- contract functions MUST exist
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict

from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.state_runtime.state_paths import contractor_projects_root


STATE_ROOT = contractor_projects_root()


# -------------------------
# helpers
# -------------------------

def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _safe_str(v: Any) -> str:
    return str(v or "").strip()


def get_baseline_lock_path(project_id: str) -> Path:
    return (
        STATE_ROOT
        / _safe_str(project_id)
        / "project_intake"
        / "baseline_lock.json"
    )


# -------------------------
# classification
# -------------------------

def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": "contractor_baseline_lock_record",
        "mutation_class": "contractor_baseline_lock_persistence",
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "state_mutation_allowed": True,
        "project_truth_mutation_allowed": True,
        "advisory_only": False,
    }


def _authority_metadata(operation: str, project_id: str) -> Dict[str, Any]:
    return {
        "authority_id": "northstar_stage_6a",
        "operation": operation,
        "child_core_id": "contractor_builder_v1",
        "layer": "project_intake.baseline_lock_runtime",
        "project_id": _safe_str(project_id),
    }


# -------------------------
# core builder
# -------------------------

def build_baseline_lock_record(
    *,
    project_id: str,
    project_name: str = "",
    created_by: str = "system",
    notes: str = "",
) -> Dict[str, Any]:

    clean_project_id = _safe_str(project_id)

    if not clean_project_id:
        raise ValueError("project_id is required")

    return {
        "artifact_type": "contractor_baseline_lock_record",
        "artifact_version": "northstar_baseline_lock_v1",
        "project_id": clean_project_id,
        "project_name": _safe_str(project_name),
        "created_by": _safe_str(created_by),
        "notes": notes,
        "locked_at": _utc_now_iso(),
        "classification": _classification_block(),
        "authority_metadata": _authority_metadata(
            "build_baseline_lock_record",
            clean_project_id,
        ),
        "sealed": True,
    }


# -------------------------
# REQUIRED CONTRACT FUNCTION
# -------------------------

def create_baseline_lock_record(
    *,
    project_id: str,
    project_name: str = "",
    created_by: str = "system",
    notes: str = "",
) -> Dict[str, Any]:
    """
    🔥 THIS is the missing function causing your system failure
    """

    return build_baseline_lock_record(
        project_id=project_id,
        project_name=project_name,
        created_by=created_by,
        notes=notes,
    )


# -------------------------
# persistence
# -------------------------

def write_baseline_lock_record(record: Dict[str, Any]) -> Path:

    if not isinstance(record, dict):
        raise ValueError("record must be a dict")

    project_id = _safe_str(record.get("project_id"))

    if not project_id:
        raise ValueError("project_id is required")

    payload = dict(record)
    payload["classification"] = _classification_block()
    payload["authority_metadata"] = _authority_metadata(
        "write_baseline_lock_record",
        project_id,
    )
    payload["sealed"] = True

    path = get_baseline_lock_path(project_id)

    governed_write_json(
        path=path,
        payload=payload,
        mutation_class="contractor_baseline_lock_persistence",
        persistence_type="contractor_baseline_lock_record",
        authority_metadata=payload["authority_metadata"],
    )

    return path