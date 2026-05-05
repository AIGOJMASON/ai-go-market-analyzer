"""
Portfolio aggregator for contractor_builder_v1.

This module groups project weekly reports into portfolio weekly reports using an
explicit portfolio -> project mapping. It is read-only aggregation only.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..report.portfolio_weekly_builder import build_portfolio_weekly_report


def aggregate_portfolio_weekly_reports(
    *,
    reporting_period_label: str,
    project_reports: List[Dict[str, Any]],
    portfolio_project_map: Dict[str, List[str]],
) -> List[Dict[str, Any]]:
    """
    Aggregate project reports into portfolio reports.
    """
    reports_by_project_id = {
        str(report.get("subject_id", "")): report for report in project_reports
    }

    portfolio_reports: List[Dict[str, Any]] = []

    for portfolio_id, project_ids in portfolio_project_map.items():
        selected_reports = [
            reports_by_project_id[project_id]
            for project_id in project_ids
            if project_id in reports_by_project_id
        ]

        if not selected_reports:
            continue

        portfolio_report = build_portfolio_weekly_report(
            portfolio_id=portfolio_id,
            reporting_period_label=reporting_period_label,
            project_reports=selected_reports,
        )
        portfolio_reports.append(portfolio_report)

    return portfolio_reports