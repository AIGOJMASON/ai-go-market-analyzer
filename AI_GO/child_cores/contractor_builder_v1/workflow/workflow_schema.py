"""
Workflow root schema for contractor_builder_v1.

This module defines the canonical workflow-level schema fragments and template
helpers used by the workflow runtime and related modules.

It owns:
- workflow schema version
- declared workflow core entity names
- canonical workflow state template

It does NOT:
- initialize workflow on disk
- reconcile phase transitions
- persist workflow history
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List

from ..governance.shared_enums import SHARED_ENUMS

WORKFLOW_SCHEMA_VERSION = "v1"

WORKFLOW_CORE_ENTITIES: List[str] = [
    "phase_template",
    "phase_instance",
    "role_expectations",
    "management_checkpoints",
    "client_gate_requirement",
    "client_signoff_record",
    "client_signoff_status_record",
    "phase_drift_record",
    "dead_time_estimate_record",
    "phase_history_log",
    "workflow_state_record",
    "workflow_checklist_record",
]

WORKFLOW_STATUS_ENUM: List[str] = [
    "initialized",
    "active",
    "blocked",
    "complete",
]


def get_workflow_record_template() -> Dict[str, Any]:
    """
    Return an empty canonical workflow state template for a project.

    This is a shape/template helper only. Runtime is responsible for:
    - created_at / updated_at values
    - current_phase_id authority
    - linked receipt updates
    - integrity hashing
    """
    return deepcopy(
        {
            "schema_version": WORKFLOW_SCHEMA_VERSION,
            "project_id": "",
            "workflow_status": "initialized",
            "phase_count": 0,
            "current_phase_id": "",
            "allowed_workflow_statuses": list(WORKFLOW_STATUS_ENUM),
            "allowed_phase_statuses": list(SHARED_ENUMS["phase_status"]),
            "created_at": "",
            "updated_at": "",
            "notes": "",
            "integrity": {
                "entry_hash": "",
                "linked_receipts": [],
            },
        }
    )