"""
Client gate schema for contractor_builder_v1.

Client gates represent phase-level visual inspection and signoff requirements.
They preserve the difference between:
- a requirement that a phase must be reviewed
- an actual client signoff event
"""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional


CLIENT_GATE_SCHEMA_VERSION = "v1"


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def build_client_gate_requirement(
    *,
    phase_id: str,
    project_id: str,
    required: bool,
    checklist: Optional[List[str]] = None,
    notes: str = "",
) -> Dict[str, Any]:
    """
    Build a canonical client gate requirement record.
    """
    return {
        "schema_version": CLIENT_GATE_SCHEMA_VERSION,
        "phase_id": phase_id,
        "project_id": project_id,
        "required": required,
        "checklist": list(checklist or []),
        "status": "not_required" if not required else "pending",
        "notes": notes,
    }


def build_client_signoff_record(
    *,
    project_id: str,
    phase_id: str,
    client_name: str,
    result: str,
    checklist_completed: Optional[List[str]] = None,
    notes: str = "",
    timestamp: str = "",
) -> Dict[str, Any]:
    """
    Build a client signoff event record.
    """
    if result not in {"approved", "denied", "conditional"}:
        raise ValueError("result must be one of: approved, denied, conditional")

    return {
        "schema_version": CLIENT_GATE_SCHEMA_VERSION,
        "project_id": project_id,
        "phase_id": phase_id,
        "client_name": client_name,
        "result": result,
        "checklist_completed": list(checklist_completed or []),
        "notes": notes,
        "timestamp": timestamp or _utc_now_iso(),
    }


def get_client_gate_requirement_template() -> Dict[str, Any]:
    return deepcopy(
        {
            "schema_version": CLIENT_GATE_SCHEMA_VERSION,
            "phase_id": "",
            "project_id": "",
            "required": False,
            "checklist": [],
            "status": "not_required",
            "notes": "",
        }
    )


def get_client_signoff_record_template() -> Dict[str, Any]:
    return deepcopy(
        {
            "schema_version": CLIENT_GATE_SCHEMA_VERSION,
            "project_id": "",
            "phase_id": "",
            "client_name": "",
            "result": "",
            "checklist_completed": [],
            "notes": "",
            "timestamp": "",
        }
    )