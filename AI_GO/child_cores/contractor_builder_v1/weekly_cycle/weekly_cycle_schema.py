"""
Weekly cycle schema for contractor_builder_v1.

This module defines the canonical orchestration record used for:
- weekly cycle execution
- project snapshot collection
- report staging
- portfolio aggregation
- receipt-linked visibility

Weekly cycle is read-only orchestration. It must not mutate upstream truth.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any, Dict, List

WEEKLY_CYCLE_SCHEMA_VERSION = "v1"

WEEKLY_CYCLE_STATUS_ENUM = [
    "draft",
    "running",
    "completed",
    "failed",
]


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def build_weekly_cycle_record(
    *,
    cycle_id: str,
    reporting_period_label: str,
    project_ids: List[str],
    portfolio_ids: List[str],
) -> Dict[str, Any]:
    """
    Build the canonical weekly cycle record.
    """
    return {
        "schema_version": WEEKLY_CYCLE_SCHEMA_VERSION,
        "cycle_id": cycle_id,
        "reporting_period_label": reporting_period_label,
        "project_ids": list(project_ids),
        "portfolio_ids": list(portfolio_ids),
        "cycle_status": "draft",
        "started_at": None,
        "completed_at": None,
        "project_report_count": 0,
        "portfolio_report_count": 0,
        "project_reports": [],
        "portfolio_reports": [],
        "errors": [],
        "notes": "",
        "generated_at": _utc_now_iso(),
        "allowed_cycle_statuses": WEEKLY_CYCLE_STATUS_ENUM,
    }


def validate_weekly_cycle_record(record: Dict[str, Any]) -> List[str]:
    """
    Validate the minimum required shape of a weekly cycle record.
    """
    errors: List[str] = []

    required_fields = [
        "cycle_id",
        "reporting_period_label",
        "project_ids",
        "portfolio_ids",
        "cycle_status",
        "project_report_count",
        "portfolio_report_count",
        "project_reports",
        "portfolio_reports",
        "errors",
        "generated_at",
    ]
    for field in required_fields:
        if field not in record:
            errors.append(f"Missing required weekly cycle field: {field}")

    if not record.get("cycle_id"):
        errors.append("cycle_id may not be empty")
    if not record.get("reporting_period_label"):
        errors.append("reporting_period_label may not be empty")

    cycle_status = record.get("cycle_status")
    if cycle_status not in WEEKLY_CYCLE_STATUS_ENUM:
        errors.append(
            f"cycle_status must be one of {WEEKLY_CYCLE_STATUS_ENUM}"
        )

    if not isinstance(record.get("project_ids", []), list):
        errors.append("project_ids must be a list")
    if not isinstance(record.get("portfolio_ids", []), list):
        errors.append("portfolio_ids must be a list")
    if not isinstance(record.get("project_reports", []), list):
        errors.append("project_reports must be a list")
    if not isinstance(record.get("portfolio_reports", []), list):
        errors.append("portfolio_reports must be a list")
    if not isinstance(record.get("errors", []), list):
        errors.append("errors must be a list")

    return errors


def get_weekly_cycle_template() -> Dict[str, Any]:
    """
    Return an empty weekly cycle template.
    """
    return deepcopy(
        {
            "schema_version": WEEKLY_CYCLE_SCHEMA_VERSION,
            "cycle_id": "",
            "reporting_period_label": "",
            "project_ids": [],
            "portfolio_ids": [],
            "cycle_status": "draft",
            "started_at": None,
            "completed_at": None,
            "project_report_count": 0,
            "portfolio_report_count": 0,
            "project_reports": [],
            "portfolio_reports": [],
            "errors": [],
            "notes": "",
            "generated_at": "",
            "allowed_cycle_statuses": WEEKLY_CYCLE_STATUS_ENUM,
        }
    )