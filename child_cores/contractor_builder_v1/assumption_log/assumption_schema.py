"""
Assumption schema for contractor_builder_v1.

This module defines the canonical structured assumption record used for:
- explicit project assumptions
- source attribution
- validation status tracking
- downstream linkage to decisions, changes, and risks
"""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from ..governance.shared_enums import SHARED_ENUMS

ASSUMPTION_SCHEMA_VERSION = "v1"

ASSUMPTION_SOURCE_TYPE_ENUM = [
    "Drawing",
    "Specification",
    "Contract",
    "Verbal",
    "Site_Visit",
    "Email",
    "Other",
]


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def build_assumption_entry(
    *,
    assumption_id: str,
    project_id: str,
    statement: str,
    source_type: str,
    source_reference: str,
    logged_by: str,
    owner_acknowledged: str = "Not_Required",
    validation_status: str = "Unverified",
    impact_if_false: str = "",
    linked_decision_ids: Optional[List[str]] = None,
    linked_change_packet_ids: Optional[List[str]] = None,
    linked_risk_ids: Optional[List[str]] = None,
    notes: str = "",
) -> Dict[str, Any]:
    """
    Build a canonical assumption entry.
    """
    if source_type not in ASSUMPTION_SOURCE_TYPE_ENUM:
        raise ValueError(
            f"source_type must be one of {ASSUMPTION_SOURCE_TYPE_ENUM}"
        )

    if owner_acknowledged not in SHARED_ENUMS["owner_acknowledged"]:
        raise ValueError(
            f"owner_acknowledged must be one of {SHARED_ENUMS['owner_acknowledged']}"
        )

    if validation_status not in SHARED_ENUMS["validation_status"]:
        raise ValueError(
            f"validation_status must be one of {SHARED_ENUMS['validation_status']}"
        )

    return {
        "schema_version": ASSUMPTION_SCHEMA_VERSION,
        "assumption_id": assumption_id,
        "project_id": project_id,
        "statement": statement,
        "source_type": source_type,
        "source_reference": source_reference,
        "date_logged": _utc_now_iso(),
        "logged_by": logged_by,
        "owner_acknowledged": owner_acknowledged,
        "validation_status": validation_status,
        "impact_if_false": impact_if_false,
        "linked_decision_ids": list(linked_decision_ids or []),
        "linked_change_packet_ids": list(linked_change_packet_ids or []),
        "linked_risk_ids": list(linked_risk_ids or []),
        "notes": notes,
        "integrity": {
            "entry_hash": "",
            "linked_receipts": [],
        },
        "allowed_source_types": ASSUMPTION_SOURCE_TYPE_ENUM,
        "allowed_validation_statuses": SHARED_ENUMS["validation_status"],
        "allowed_owner_acknowledged": SHARED_ENUMS["owner_acknowledged"],
    }


def validate_assumption_entry(entry: Dict[str, Any]) -> List[str]:
    """
    Validate the minimum required shape of an assumption entry.
    """
    errors: List[str] = []

    required_fields = [
        "assumption_id",
        "project_id",
        "statement",
        "source_type",
        "source_reference",
        "date_logged",
        "logged_by",
        "owner_acknowledged",
        "validation_status",
        "impact_if_false",
        "linked_decision_ids",
        "linked_change_packet_ids",
        "linked_risk_ids",
        "notes",
        "integrity",
    ]
    for field in required_fields:
        if field not in entry:
            errors.append(f"Missing required assumption field: {field}")

    if not entry.get("assumption_id"):
        errors.append("assumption_id may not be empty")
    if not entry.get("project_id"):
        errors.append("project_id may not be empty")
    if not entry.get("statement"):
        errors.append("statement may not be empty")
    if not entry.get("source_reference"):
        errors.append("source_reference may not be empty")
    if not entry.get("logged_by"):
        errors.append("logged_by may not be empty")

    source_type = entry.get("source_type")
    if source_type not in ASSUMPTION_SOURCE_TYPE_ENUM:
        errors.append(f"source_type must be one of {ASSUMPTION_SOURCE_TYPE_ENUM}")

    owner_acknowledged = entry.get("owner_acknowledged")
    if owner_acknowledged not in SHARED_ENUMS["owner_acknowledged"]:
        errors.append(
            f"owner_acknowledged must be one of {SHARED_ENUMS['owner_acknowledged']}"
        )

    validation_status = entry.get("validation_status")
    if validation_status not in SHARED_ENUMS["validation_status"]:
        errors.append(
            f"validation_status must be one of {SHARED_ENUMS['validation_status']}"
        )

    return errors


def get_assumption_entry_template() -> Dict[str, Any]:
    """
    Return an empty assumption entry template.
    """
    return deepcopy(
        {
            "schema_version": ASSUMPTION_SCHEMA_VERSION,
            "assumption_id": "",
            "project_id": "",
            "statement": "",
            "source_type": "",
            "source_reference": "",
            "date_logged": "",
            "logged_by": "",
            "owner_acknowledged": "Not_Required",
            "validation_status": "Unverified",
            "impact_if_false": "",
            "linked_decision_ids": [],
            "linked_change_packet_ids": [],
            "linked_risk_ids": [],
            "notes": "",
            "integrity": {
                "entry_hash": "",
                "linked_receipts": [],
            },
            "allowed_source_types": ASSUMPTION_SOURCE_TYPE_ENUM,
            "allowed_validation_statuses": SHARED_ENUMS["validation_status"],
            "allowed_owner_acknowledged": SHARED_ENUMS["owner_acknowledged"],
        }
    )