"""
Project weekly builder for contractor_builder_v1.

This module assembles a project weekly report from structured deterministic inputs.
It does not invent upstream truth and does not approve the report.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..governance.identity import build_report_id
from ..governance.integrity import compute_hash_for_mapping
from .report_schema import build_report_shell, validate_report_record
from .deterministic_block_builder import build_project_deterministic_block
from .summary_draft_builder import build_project_summary_draft


def build_project_weekly_report(
    *,
    project_id: str,
    reporting_period_label: str,
    workflow_snapshot: Dict[str, Any],
    change_records: List[Dict[str, Any]],
    compliance_snapshot: Dict[str, Any],
    router_snapshot: Dict[str, Any],
    oracle_snapshot: Dict[str, Any],
    decision_records: List[Dict[str, Any]],
    risk_records: List[Dict[str, Any]],
    assumption_records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Build a complete project weekly report from deterministic source inputs.
    """
    report_id = build_report_id(project_id, "project_weekly")

    report = build_report_shell(
        report_id=report_id,
        report_type="Project_Weekly",
        subject_id=project_id,
        reporting_period_label=reporting_period_label,
    )

    deterministic_block = build_project_deterministic_block(
        project_id=project_id,
        workflow_snapshot=workflow_snapshot,
        change_records=change_records,
        compliance_snapshot=compliance_snapshot,
        router_snapshot=router_snapshot,
        oracle_snapshot=oracle_snapshot,
        decision_records=decision_records,
        risk_records=risk_records,
        assumption_records=assumption_records,
    )

    summary_draft = build_project_summary_draft(
        project_id=project_id,
        reporting_period_label=reporting_period_label,
        deterministic_block=deterministic_block,
    )

    report["deterministic_block"] = deterministic_block
    report["summary_draft"] = summary_draft
    report["report_status"] = "pm_review"

    report["integrity"]["entry_hash"] = compute_hash_for_mapping(
        {
            key: value
            for key, value in report.items()
            if key != "integrity"
        }
    )

    errors = validate_report_record(report)
    if errors:
        raise ValueError("Invalid project weekly report: " + "; ".join(errors))

    return report