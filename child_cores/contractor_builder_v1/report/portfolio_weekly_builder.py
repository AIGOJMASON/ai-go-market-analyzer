"""
Portfolio weekly builder for contractor_builder_v1.

This module assembles a portfolio weekly report from a list of project weekly
deterministic blocks. It is read-only aggregation only.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..governance.identity import build_report_id
from ..governance.integrity import compute_hash_for_mapping
from .report_schema import build_report_shell, validate_report_record
from .deterministic_block_builder import build_portfolio_deterministic_block
from .summary_draft_builder import build_portfolio_summary_draft


def build_portfolio_weekly_report(
    *,
    portfolio_id: str,
    reporting_period_label: str,
    project_reports: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Build a portfolio weekly report from project weekly reports.
    """
    report_id = build_report_id(portfolio_id, "portfolio_weekly")

    report = build_report_shell(
        report_id=report_id,
        report_type="Portfolio_Weekly",
        subject_id=portfolio_id,
        reporting_period_label=reporting_period_label,
    )

    deterministic_block = build_portfolio_deterministic_block(
        portfolio_id=portfolio_id,
        project_reports=project_reports,
    )

    summary_draft = build_portfolio_summary_draft(
        portfolio_id=portfolio_id,
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
        raise ValueError("Invalid portfolio weekly report: " + "; ".join(errors))

    return report