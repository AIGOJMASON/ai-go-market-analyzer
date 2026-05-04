"""
Weekly report interpreter for contractor_builder_v1.

This module interprets structured weekly report artifacts into bounded plain-language
reads. It must only use fields already present in the report.
"""

from __future__ import annotations

from typing import Any, Dict, List


def interpret_project_weekly_report(report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Interpret a project weekly report in bounded plain language.
    """
    summary_draft = report.get("summary_draft", {})
    deterministic_block = report.get("deterministic_block", {})

    workflow = deterministic_block.get("workflow", {})
    change = deterministic_block.get("change", {})
    compliance = deterministic_block.get("compliance", {})
    router = deterministic_block.get("router", {})
    oracle = deterministic_block.get("oracle", {})
    risk = deterministic_block.get("risk", {})
    assumption = deterministic_block.get("assumption", {})

    plain_read = (
        f"Weekly project report for {report.get('subject_id', '')}. "
        f"Workflow status is {workflow.get('workflow_status', '')}. "
        f"Approved changes total {change.get('approved_change_total_amount', 0.0)}. "
        f"Compliance blocking is {compliance.get('blocking', False)}. "
        f"Router conflicts are {router.get('conflict_count', 0)}. "
        f"External pressure summary is {oracle.get('summary_label', '')}. "
        f"Open or monitoring risks are {risk.get('open_or_monitoring_count', 0)}. "
        f"Invalidated assumptions are {assumption.get('invalidated_count', 0)}."
    )

    return {
        "headline": summary_draft.get("headline", ""),
        "bullets": list(summary_draft.get("bullets", [])),
        "plain_read": plain_read,
    }


def interpret_portfolio_weekly_report(report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Interpret a portfolio weekly report in bounded plain language.
    """
    summary_draft = report.get("summary_draft", {})
    deterministic_block = report.get("deterministic_block", {})

    plain_read = (
        f"Weekly portfolio report for {report.get('subject_id', '')}. "
        f"Project count is {deterministic_block.get('project_count', 0)}. "
        f"Blocking project count is {deterministic_block.get('blocking_project_count', 0)}. "
        f"Total conflict count is {deterministic_block.get('total_conflict_count', 0)}. "
        f"Total open or monitoring risks are {deterministic_block.get('total_open_or_monitoring_risks', 0)}. "
        f"Approved change total amount is {deterministic_block.get('approved_change_total_amount', 0.0)}."
    )

    return {
        "headline": summary_draft.get("headline", ""),
        "bullets": list(summary_draft.get("bullets", [])),
        "plain_read": plain_read,
    }