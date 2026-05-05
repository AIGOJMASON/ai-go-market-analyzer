"""
Report schema for contractor_builder_v1.

This module defines the canonical report contract used for:
- project weekly reports
- portfolio weekly reports
- deterministic numbers-first blocks
- bounded summary drafts
- PM-gated approval and archival

Reports are projection/orchestration artifacts. They do not mutate upstream truth.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any, Dict, List

REPORT_SCHEMA_VERSION = "v1"

REPORT_TYPE_ENUM = [
    "Project_Weekly",
    "Portfolio_Weekly",
]

REPORT_STATUS_ENUM = [
    "draft",
    "pm_review",
    "approved",
    "archived",
]


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def build_report_shell(
    *,
    report_id: str,
    report_type: str,
    subject_id: str,
    reporting_period_label: str,
) -> Dict[str, Any]:
    """
    Build the canonical shell for a contractor report.
    """
    if report_type not in REPORT_TYPE_ENUM:
        raise ValueError(f"report_type must be one of {REPORT_TYPE_ENUM}")

    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_id": report_id,
        "report_type": report_type,
        "subject_id": subject_id,
        "reporting_period_label": reporting_period_label,
        "report_status": "draft",
        "generated_at": _utc_now_iso(),
        "deterministic_block": {},
        "summary_draft": {
            "headline": "",
            "bullets": [],
            "notes": "",
        },
        "pm_approval": {
            "approved_by": "",
            "approved_at": None,
            "approval_notes": "",
            "signature": None,
        },
        "integrity": {
            "entry_hash": "",
            "linked_receipts": [],
        },
        "allowed_report_types": REPORT_TYPE_ENUM,
        "allowed_report_statuses": REPORT_STATUS_ENUM,
    }


def validate_report_record(record: Dict[str, Any]) -> List[str]:
    """
    Validate the minimum required shape of a report record.
    """
    errors: List[str] = []

    required_fields = [
        "report_id",
        "report_type",
        "subject_id",
        "reporting_period_label",
        "report_status",
        "generated_at",
        "deterministic_block",
        "summary_draft",
        "pm_approval",
        "integrity",
    ]
    for field in required_fields:
        if field not in record:
            errors.append(f"Missing required report field: {field}")

    if not record.get("report_id"):
        errors.append("report_id may not be empty")
    if not record.get("subject_id"):
        errors.append("subject_id may not be empty")
    if not record.get("reporting_period_label"):
        errors.append("reporting_period_label may not be empty")

    report_type = record.get("report_type")
    if report_type not in REPORT_TYPE_ENUM:
        errors.append(f"report_type must be one of {REPORT_TYPE_ENUM}")

    report_status = record.get("report_status")
    if report_status not in REPORT_STATUS_ENUM:
        errors.append(f"report_status must be one of {REPORT_STATUS_ENUM}")

    if not isinstance(record.get("deterministic_block", {}), dict):
        errors.append("deterministic_block must be a mapping")

    summary_draft = record.get("summary_draft", {})
    if not isinstance(summary_draft, dict):
        errors.append("summary_draft must be a mapping")
    else:
        if "headline" not in summary_draft:
            errors.append("summary_draft.headline is required")
        if "bullets" not in summary_draft:
            errors.append("summary_draft.bullets is required")

    if not isinstance(record.get("pm_approval", {}), dict):
        errors.append("pm_approval must be a mapping")

    return errors


def get_report_template() -> Dict[str, Any]:
    """
    Return an empty contractor report template.
    """
    return deepcopy(
        {
            "schema_version": REPORT_SCHEMA_VERSION,
            "report_id": "",
            "report_type": "",
            "subject_id": "",
            "reporting_period_label": "",
            "report_status": "draft",
            "generated_at": "",
            "deterministic_block": {},
            "summary_draft": {
                "headline": "",
                "bullets": [],
                "notes": "",
            },
            "pm_approval": {
                "approved_by": "",
                "approved_at": None,
                "approval_notes": "",
                "signature": None,
            },
            "integrity": {
                "entry_hash": "",
                "linked_receipts": [],
            },
            "allowed_report_types": REPORT_TYPE_ENUM,
            "allowed_report_statuses": REPORT_STATUS_ENUM,
        }
    )