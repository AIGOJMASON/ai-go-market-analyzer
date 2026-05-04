"""
Portfolio projection for contractor_builder_v1.

This module builds the read-only portfolio-facing panel used by the operator payload.
"""

from __future__ import annotations

from typing import Any, Dict


def build_portfolio_projection(
    *,
    portfolio_report: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build the portfolio-facing projection block.
    """
    deterministic_block = portfolio_report.get("deterministic_block", {})
    summary_draft = portfolio_report.get("summary_draft", {})

    return {
        "portfolio_id": portfolio_report.get("subject_id", ""),
        "report_id": portfolio_report.get("report_id", ""),
        "report_status": portfolio_report.get("report_status", ""),
        "reporting_period_label": portfolio_report.get("reporting_period_label", ""),
        "headline": summary_draft.get("headline", ""),
        "bullets": list(summary_draft.get("bullets", [])),
        "portfolio_metrics": {
            "project_count": deterministic_block.get("project_count", 0),
            "blocking_project_count": deterministic_block.get("blocking_project_count", 0),
            "total_conflict_count": deterministic_block.get("total_conflict_count", 0),
            "total_open_or_monitoring_risks": deterministic_block.get(
                "total_open_or_monitoring_risks", 0
            ),
            "approved_change_total_amount": deterministic_block.get(
                "approved_change_total_amount", 0.0
            ),
        },
    }