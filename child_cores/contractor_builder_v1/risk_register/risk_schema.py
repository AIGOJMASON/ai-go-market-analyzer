"""
Risk schema for contractor_builder_v1.

This module defines the canonical human-centered operational risk record used for:
- append-only project risk tracking
- human judgment-led probability and impact labeling
- weekly review posture
- linkage to decisions and change packets
"""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from ..governance.shared_enums import SHARED_ENUMS

RISK_SCHEMA_VERSION = "v1"

RISK_CATEGORY_ENUM = [
    "Site_Conditions",
    "Design_Ambiguity",
    "Owner_Behavior",
    "Vendor_Stability",
    "Material_Availability",
    "Permit_Inspection",
    "Weather_Exposure",
    "Access_Logistics",
    "Utility_Conflict",
    "Legal_Insurance",
    "Neighborhood_Public",
    "Other",
]


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def build_risk_entry(
    *,
    risk_id: str,
    project_id: str,
    category: str,
    description: str,
    probability: str,
    impact_level: str,
    mitigation_strategy: str,
    mitigation_owner: str,
    review_frequency: str = "weekly",
    linked_decision_ids: Optional[List[str]] = None,
    linked_change_packet_ids: Optional[List[str]] = None,
    notes: str = "",
) -> Dict[str, Any]:
    """
    Build a canonical draft risk entry.
    """
    if category not in RISK_CATEGORY_ENUM:
        raise ValueError(f"category must be one of {RISK_CATEGORY_ENUM}")

    if probability not in SHARED_ENUMS["probability_level"]:
        raise ValueError(
            f"probability must be one of {SHARED_ENUMS['probability_level']}"
        )

    if impact_level not in SHARED_ENUMS["impact_level"]:
        raise ValueError(
            f"impact_level must be one of {SHARED_ENUMS['impact_level']}"
        )

    return {
        "schema_version": RISK_SCHEMA_VERSION,
        "risk_id": risk_id,
        "project_id": project_id,
        "category": category,
        "description": description,
        "probability": probability,
        "impact_level": impact_level,
        "mitigation_strategy": mitigation_strategy,
        "mitigation_owner": mitigation_owner,
        "review_frequency": review_frequency,
        "status": "Open",
        "date_logged": _utc_now_iso(),
        "last_reviewed": "",
        "linked_decision_ids": list(linked_decision_ids or []),
        "linked_change_packet_ids": list(linked_change_packet_ids or []),
        "notes": notes,
        "integrity": {
            "entry_hash": "",
            "linked_receipts": [],
        },
        "allowed_categories": RISK_CATEGORY_ENUM,
        "allowed_probability": SHARED_ENUMS["probability_level"],
        "allowed_impact": SHARED_ENUMS["impact_level"],
        "allowed_statuses": SHARED_ENUMS["risk_status"],
    }


def validate_risk_entry(entry: Dict[str, Any]) -> List[str]:
    """
    Validate the minimum required shape of a risk entry.
    """
    errors: List[str] = []

    required_fields = [
        "risk_id",
        "project_id",
        "category",
        "description",
        "probability",
        "impact_level",
        "mitigation_strategy",
        "mitigation_owner",
        "review_frequency",
        "status",
        "date_logged",
        "last_reviewed",
        "linked_decision_ids",
        "linked_change_packet_ids",
        "notes",
        "integrity",
    ]
    for field in required_fields:
        if field not in entry:
            errors.append(f"Missing required risk field: {field}")

    if not entry.get("risk_id"):
        errors.append("risk_id may not be empty")
    if not entry.get("project_id"):
        errors.append("project_id may not be empty")
    if not entry.get("description"):
        errors.append("description may not be empty")
    if not entry.get("mitigation_strategy"):
        errors.append("mitigation_strategy may not be empty")
    if not entry.get("mitigation_owner"):
        errors.append("mitigation_owner may not be empty")

    category = entry.get("category")
    if category not in RISK_CATEGORY_ENUM:
        errors.append(f"category must be one of {RISK_CATEGORY_ENUM}")

    probability = entry.get("probability")
    if probability not in SHARED_ENUMS["probability_level"]:
        errors.append(
            f"probability must be one of {SHARED_ENUMS['probability_level']}"
        )

    impact_level = entry.get("impact_level")
    if impact_level not in SHARED_ENUMS["impact_level"]:
        errors.append(
            f"impact_level must be one of {SHARED_ENUMS['impact_level']}"
        )

    status = entry.get("status")
    if status not in SHARED_ENUMS["risk_status"]:
        errors.append(f"status must be one of {SHARED_ENUMS['risk_status']}")

    return errors


def get_risk_entry_template() -> Dict[str, Any]:
    """
    Return an empty risk entry template.
    """
    return deepcopy(
        {
            "schema_version": RISK_SCHEMA_VERSION,
            "risk_id": "",
            "project_id": "",
            "category": "",
            "description": "",
            "probability": "",
            "impact_level": "",
            "mitigation_strategy": "",
            "mitigation_owner": "",
            "review_frequency": "weekly",
            "status": "Open",
            "date_logged": "",
            "last_reviewed": "",
            "linked_decision_ids": [],
            "linked_change_packet_ids": [],
            "notes": "",
            "integrity": {
                "entry_hash": "",
                "linked_receipts": [],
            },
            "allowed_categories": RISK_CATEGORY_ENUM,
            "allowed_probability": SHARED_ENUMS["probability_level"],
            "allowed_impact": SHARED_ENUMS["impact_level"],
            "allowed_statuses": SHARED_ENUMS["risk_status"],
        }
    )