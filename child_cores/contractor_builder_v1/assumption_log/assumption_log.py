"""
Assumption log compatibility surface for contractor_builder_v1.

This module preserves the legacy assumption_log import surface while routing all
append-only assumption persistence through governed_persistence.

Northstar Stage 6A rule:
No direct filesystem mutation calls are permitted.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from AI_GO.core.governance.governed_persistence import governed_append_jsonl
from AI_GO.core.state_runtime.state_paths import contractor_projects_root

from ..governance.integrity import compute_hash_for_mapping
from .assumption_schema import build_assumption_entry, validate_assumption_entry


STATE_ROOT = contractor_projects_root()


def get_assumptions_path(project_id: str) -> Path:
    """
    Return the canonical assumptions log path for a project.
    """
    return STATE_ROOT / project_id / "assumption_log" / "assumptions.jsonl"


def _authority_metadata(operation: str, project_id: str = "") -> Dict[str, Any]:
    return {
        "authority_id": "northstar_stage_6a",
        "operation": operation,
        "child_core_id": "contractor_builder_v1",
        "layer": "assumption_log.assumption_log",
        "project_id": str(project_id or "").strip(),
    }


def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": "contractor_assumption_log_record",
        "mutation_class": "contractor_assumption_log_persistence",
        "advisory_only": False,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "state_mutation_allowed": True,
        "append_only": True,
    }


def _authority_block() -> Dict[str, Any]:
    return {
        "authority_id": "contractor_assumption_log",
        "can_execute": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
        "can_write_outside_governed_persistence": False,
        "state_authority": "governed_append_only",
    }


def _refresh_assumption_integrity(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Refresh the assumption entry hash while preserving linked receipt metadata.
    """
    updated = dict(entry)
    integrity = dict(updated.get("integrity", {}))

    entry_for_hash = dict(updated)
    entry_for_hash["integrity"] = {
        "entry_hash": "",
        "linked_receipts": integrity.get("linked_receipts", []),
    }

    integrity["entry_hash"] = compute_hash_for_mapping(entry_for_hash)
    updated["integrity"] = integrity
    return updated


def _prepare_entry_for_persistence(entry: Dict[str, Any]) -> Dict[str, Any]:
    entry_to_write = _refresh_assumption_integrity(entry)
    entry_to_write.setdefault("classification", _classification_block())
    entry_to_write.setdefault("authority", _authority_block())
    entry_to_write.setdefault("sealed", True)
    return entry_to_write


def create_assumption_record(**kwargs: Any) -> Dict[str, Any]:
    """
    Create a canonical assumption record and compute integrity.
    """
    entry = build_assumption_entry(**kwargs)
    errors = validate_assumption_entry(entry)
    if errors:
        raise ValueError("Invalid assumption entry: " + "; ".join(errors))
    return _refresh_assumption_integrity(entry)


def append_assumption_record(
    entry: Dict[str, Any],
    *,
    create_dirs: bool = True,
) -> Path:
    """
    Append an assumption entry to the project assumptions log.
    """
    errors = validate_assumption_entry(entry)
    if errors:
        raise ValueError("Invalid assumption entry: " + "; ".join(errors))

    project_id = str(entry["project_id"]).strip()
    output_path = get_assumptions_path(project_id)

    entry_to_write = _prepare_entry_for_persistence(entry)

    governed_append_jsonl(
        path=output_path,
        payload=entry_to_write,
        mutation_class="contractor_assumption_log_persistence",
        persistence_type="contractor_assumption_log_record",
        authority_metadata=_authority_metadata(
            operation="append_assumption_record",
            project_id=project_id,
        ),
    )

    return output_path


def transition_assumption_status(
    entry: Dict[str, Any],
    *,
    new_status: str,
    notes: str = "",
) -> Dict[str, Any]:
    """
    Return a copy of the assumption entry with updated validation status.
    """
    updated = dict(entry)
    updated["validation_status"] = new_status

    existing_notes = str(updated.get("notes", "") or "")
    if notes:
        updated["notes"] = existing_notes + ("\n" if existing_notes else "") + notes

    return _refresh_assumption_integrity(updated)
