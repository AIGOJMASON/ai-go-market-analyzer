"""
Schedule block runtime for contractor_builder_v1.

This module creates, validates, persists, and loads schedule block records.

Northstar Stage 6A rule:
All runtime persistence must go through governed_persistence.
No direct json.dump, .write, .write_text, or .write_bytes calls.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.state_runtime.state_paths import contractor_projects_root

from .router_schema import build_schedule_block, validate_schedule_block


STATE_ROOT = contractor_projects_root()


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def get_schedule_blocks_path(project_id: str) -> Path:
    """
    Return the canonical schedule blocks file path for a project.

    This preserves the original base-code contract.
    """
    return STATE_ROOT / _safe_str(project_id) / "router" / "schedule_blocks.json"


def get_schedule_block_path(project_id: str, block_id: str) -> Path:
    """
    Return an optional per-block record path.

    Kept for compatibility with newer code that asks for a single block path.
    """
    return (
        STATE_ROOT
        / _safe_str(project_id)
        / "router"
        / "schedule_blocks"
        / f"{_safe_str(block_id)}.json"
    )


def _classification_block() -> Dict[str, Any]:
    return {
        "persistence_type": "contractor_schedule_block_record",
        "mutation_class": "contractor_schedule_block_persistence",
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "authority_mutation_allowed": False,
        "state_mutation_allowed": True,
        "workflow_mutation_allowed": False,
        "project_truth_mutation_allowed": False,
        "advisory_only": True,
    }


def _authority_metadata(
    *,
    operation: str,
    project_id: str = "",
    block_id: str = "",
) -> Dict[str, Any]:
    return {
        "authority_id": "northstar_stage_6a",
        "operation": operation,
        "child_core_id": "contractor_builder_v1",
        "layer": "router.schedule_block_runtime",
        "project_id": _safe_str(project_id),
        "block_id": _safe_str(block_id),
    }


def _stamp_block(block: Dict[str, Any]) -> Dict[str, Any]:
    stamped = dict(block)
    stamped["classification"] = _classification_block()
    stamped["authority_metadata"] = _authority_metadata(
        operation="stamp_schedule_block",
        project_id=_safe_str(stamped.get("project_id")),
        block_id=_safe_str(stamped.get("block_id")),
    )
    stamped["sealed"] = True
    return stamped


def create_schedule_block_record(**kwargs: Any) -> Dict[str, Any]:
    """
    Create and validate a schedule block record.

    This is the original public contract expected by router imports.
    """
    block = build_schedule_block(**kwargs)
    errors = validate_schedule_block(block)
    if errors:
        raise ValueError("Invalid schedule block: " + "; ".join(errors))
    return _stamp_block(block)


def upsert_schedule_blocks(
    *,
    project_id: str,
    blocks: List[Dict[str, Any]],
    create_dirs: bool = True,
) -> Path:
    """
    Persist the current schedule block set for a project.

    This preserves the original base-code behavior but uses governed persistence.
    """
    clean_project_id = _safe_str(project_id)
    if not clean_project_id:
        raise ValueError("project_id is required")

    stamped_blocks: List[Dict[str, Any]] = []

    for block in blocks:
        if not isinstance(block, dict):
            raise ValueError("Invalid schedule block: block must be a dict")

        errors = validate_schedule_block(block)
        if errors:
            raise ValueError("Invalid schedule block: " + "; ".join(errors))

        stamped_blocks.append(_stamp_block(block))

    output_path = get_schedule_blocks_path(clean_project_id)

    payload = {
        "artifact_type": "contractor_schedule_blocks",
        "artifact_version": "northstar_schedule_blocks_v1",
        "project_id": clean_project_id,
        "block_count": len(stamped_blocks),
        "blocks": stamped_blocks,
        "classification": _classification_block(),
        "authority_metadata": _authority_metadata(
            operation="upsert_schedule_blocks",
            project_id=clean_project_id,
        ),
        "sealed": True,
    }

    governed_write_json(
        path=output_path,
        payload=payload,
        mutation_class="contractor_schedule_block_persistence",
        persistence_type="contractor_schedule_block_record",
        authority_metadata=payload["authority_metadata"],
    )

    return output_path


def write_schedule_block(block: Dict[str, Any]) -> Path:
    """
    Persist one schedule block as an individual record.

    Kept for compatibility with newer per-block callers.
    """
    if not isinstance(block, dict):
        raise ValueError("block must be a dict")

    project_id = _safe_str(block.get("project_id"))
    block_id = _safe_str(block.get("block_id"))

    if not project_id:
        raise ValueError("project_id is required")
    if not block_id:
        raise ValueError("block_id is required")

    errors = validate_schedule_block(block)
    if errors:
        raise ValueError("Invalid schedule block: " + "; ".join(errors))

    payload = _stamp_block(block)
    payload["authority_metadata"] = _authority_metadata(
        operation="write_schedule_block",
        project_id=project_id,
        block_id=block_id,
    )

    output_path = get_schedule_block_path(project_id, block_id)

    governed_write_json(
        path=output_path,
        payload=payload,
        mutation_class="contractor_schedule_block_persistence",
        persistence_type="contractor_schedule_block_record",
        authority_metadata=payload["authority_metadata"],
    )

    return output_path


def load_schedule_blocks(project_id: str) -> List[Dict[str, Any]]:
    """
    Load the current schedule blocks for a project.

    Preserves original public contract.
    """
    input_path = get_schedule_blocks_path(project_id)
    if not input_path.exists():
        return []

    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except Exception:
        return []

    if isinstance(payload, dict):
        blocks = payload.get("blocks", [])
        return [dict(item) for item in blocks if isinstance(item, dict)]

    if isinstance(payload, list):
        return [dict(item) for item in payload if isinstance(item, dict)]

    return []


def list_schedule_blocks(project_id: str) -> List[Dict[str, Any]]:
    """
    Compatibility alias for newer router code.
    """
    return load_schedule_blocks(project_id)