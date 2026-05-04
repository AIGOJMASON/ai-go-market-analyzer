"""
Project report orchestrator for contractor_builder_v1.

This module is the narrow orchestration boundary between collected project snapshots
and the report builder. It does not invent data and does not approve reports.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..report.project_weekly_builder import build_project_weekly_report


def orchestrate_project_weekly_report(
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
    Build one project weekly report from bounded snapshot inputs.
    """
    return build_project_weekly_report(
        project_id=project_id,
        reporting_period_label=reporting_period_label,
        workflow_snapshot=workflow_snapshot,
        change_records=change_records,
        compliance_snapshot=compliance_snapshot,
        router_snapshot=router_snapshot,
        oracle_snapshot=oracle_snapshot,
        decision_records=decision_records,
        risk_records=risk_records,
        assumption_records=assumption_records,
    )