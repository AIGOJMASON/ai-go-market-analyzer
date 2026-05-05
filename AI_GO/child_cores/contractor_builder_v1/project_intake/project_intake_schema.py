"""
Project intake schema for contractor_builder_v1.

This module defines the canonical input contract for creating a contractor project.
The intake payload is intentionally minimal but sufficient to establish:
- project identity
- owner / PM references
- baseline budget and schedule references
- initial compliance locking reference
- optional oracle exposure reference
"""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any, Dict, List


PROJECT_INTAKE_SCHEMA_VERSION = "v1"


REQUIRED_TOP_LEVEL_FIELDS: List[str] = [
    "project_name",
    "project_type",
    "client_name",
    "pm_name",
    "jurisdiction",
    "baseline_refs",
]

REQUIRED_BASELINE_FIELDS: List[str] = [
    "schedule_baseline_id",
    "budget_baseline_id",
    "compliance_snapshot_id",
]

OPTIONAL_TOP_LEVEL_FIELDS: List[str] = [
    "project_description",
    "client_contact",
    "pm_contact",
    "site_address",
    "portfolio_id",
    "oracle_snapshot_id",
    "exposure_profile_id",
    "notes",
]


def _utc_now_iso() -> str:
    """
    Return current UTC time in ISO-8601 format.
    """
    return datetime.now(UTC).isoformat()


def build_project_intake_payload(
    *,
    project_name: str,
    project_type: str,
    client_name: str,
    pm_name: str,
    jurisdiction: Dict[str, Any],
    baseline_refs: Dict[str, Any],
    project_description: str = "",
    client_contact: str = "",
    pm_contact: str = "",
    site_address: str = "",
    portfolio_id: str = "",
    oracle_snapshot_id: str = "",
    exposure_profile_id: str = "",
    notes: str = "",
) -> Dict[str, Any]:
    """
    Build a canonical intake payload with the required shape.
    """
    payload: Dict[str, Any] = {
        "schema_version": PROJECT_INTAKE_SCHEMA_VERSION,
        "created_at": _utc_now_iso(),
        "project_name": project_name,
        "project_type": project_type,
        "project_description": project_description,
        "client_name": client_name,
        "client_contact": client_contact,
        "pm_name": pm_name,
        "pm_contact": pm_contact,
        "site_address": site_address,
        "portfolio_id": portfolio_id,
        "jurisdiction": {
            "jurisdiction_id": jurisdiction.get("jurisdiction_id", ""),
            "authority_name": jurisdiction.get("authority_name", ""),
            "city": jurisdiction.get("city", ""),
            "county": jurisdiction.get("county", ""),
            "state": jurisdiction.get("state", ""),
        },
        "baseline_refs": {
            "schedule_baseline_id": baseline_refs.get("schedule_baseline_id", ""),
            "budget_baseline_id": baseline_refs.get("budget_baseline_id", ""),
            "compliance_snapshot_id": baseline_refs.get("compliance_snapshot_id", ""),
            "oracle_snapshot_id": oracle_snapshot_id,
            "exposure_profile_id": exposure_profile_id,
        },
        "notes": notes,
    }
    return payload


def validate_project_intake_payload(payload: Dict[str, Any]) -> List[str]:
    """
    Validate the minimum required contractor intake payload shape.

    Returns:
        A list of validation errors. Empty list means valid enough to proceed.
    """
    errors: List[str] = []

    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in payload:
            errors.append(f"Missing required top-level field: {field}")

    if "baseline_refs" in payload and isinstance(payload["baseline_refs"], dict):
        for field in REQUIRED_BASELINE_FIELDS:
            if not payload["baseline_refs"].get(field):
                errors.append(f"Missing required baseline reference: {field}")
    else:
        errors.append("baseline_refs must be a mapping")

    jurisdiction = payload.get("jurisdiction")
    if not isinstance(jurisdiction, dict):
        errors.append("jurisdiction must be a mapping")
    else:
        if not jurisdiction.get("jurisdiction_id"):
            errors.append("Missing required jurisdiction field: jurisdiction_id")
        if not jurisdiction.get("state"):
            errors.append("Missing required jurisdiction field: state")

    if not payload.get("project_name"):
        errors.append("project_name may not be empty")

    if not payload.get("project_type"):
        errors.append("project_type may not be empty")

    if not payload.get("client_name"):
        errors.append("client_name may not be empty")

    if not payload.get("pm_name"):
        errors.append("pm_name may not be empty")

    return errors


def get_project_intake_template() -> Dict[str, Any]:
    """
    Return an empty intake template with the canonical shape.
    """
    return deepcopy(
        {
            "schema_version": PROJECT_INTAKE_SCHEMA_VERSION,
            "created_at": "",
            "project_name": "",
            "project_type": "",
            "project_description": "",
            "client_name": "",
            "client_contact": "",
            "pm_name": "",
            "pm_contact": "",
            "site_address": "",
            "portfolio_id": "",
            "jurisdiction": {
                "jurisdiction_id": "",
                "authority_name": "",
                "city": "",
                "county": "",
                "state": "",
            },
            "baseline_refs": {
                "schedule_baseline_id": "",
                "budget_baseline_id": "",
                "compliance_snapshot_id": "",
                "oracle_snapshot_id": "",
                "exposure_profile_id": "",
            },
            "notes": "",
        }
    )