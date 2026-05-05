"""
Summary draft builder for contractor_builder_v1.

This module builds bounded summary drafts from deterministic structured fields only.
It must not invent numbers or unsupported facts.
"""

from __future__ import annotations

from typing import Any, Dict, List


def build_project_summary_draft(
    *,
    project_id: str,
    reporting_period_label: str,
    deterministic_block: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a bounded project report summary draft from structured fields only.
    """
    compliance = deterministic_block.get("compliance", {})
    router = deterministic_block.get("router", {})
    oracle = deterministic_block.get("oracle", {})
    change = deterministic_block.get("change", {})
    risk = deterministic_block.get("risk", {})
    assumption = deterministic_block.get("assumption", {})

    headline_parts: List[str] = [f"Weekly project summary for {project_id}"]

    if compliance.get("blocking"):
        headline_parts.append("compliance blocking is active")
    elif router.get("conflict_count", 0) > 0:
        headline_parts.append("routing pressure requires attention")
    elif oracle.get("summary_label") == "elevated_external_pressure":
        headline_parts.append("external market pressure is elevated")
    else:
        headline_parts.append("no dominant blocking condition is active")

    bullets = [
        (
            f"Approved changes: {change.get('approved_change_count', 0)} "
            f"with approved total amount {change.get('approved_change_total_amount', 0.0)}."
        ),
        (
            f"Compliance blocking count: {compliance.get('blocking_count', 0)}. "
            f"Router conflicts: {router.get('conflict_count', 0)}."
        ),
        (
            f"Open or monitoring risks: {risk.get('open_or_monitoring_count', 0)}. "
            f"Invalidated assumptions: {assumption.get('invalidated_count', 0)}."
        ),
        (
            f"External pressure summary: {oracle.get('summary_label', '')}. "
            f"High-pressure domains: {oracle.get('high_domain_count', 0)}."
        ),
    ]

    return {
        "headline": " | ".join(headline_parts),
        "bullets": bullets,
        "notes": f"Reporting period: {reporting_period_label}",
    }


def build_portfolio_summary_draft(
    *,
    portfolio_id: str,
    reporting_period_label: str,
    deterministic_block: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a bounded portfolio report summary draft from structured fields only.
    """
    headline = (
        f"Weekly portfolio summary for {portfolio_id} | "
        f"projects: {deterministic_block.get('project_count', 0)}"
    )

    bullets = [
        (
            f"Blocking projects: {deterministic_block.get('blocking_project_count', 0)}. "
            f"Total conflicts: {deterministic_block.get('total_conflict_count', 0)}."
        ),
        (
            f"Total open or monitoring risks: "
            f"{deterministic_block.get('total_open_or_monitoring_risks', 0)}."
        ),
        (
            f"Approved change total amount: "
            f"{deterministic_block.get('approved_change_total_amount', 0.0)}."
        ),
        (
            f"Projects under elevated external pressure: "
            f"{deterministic_block.get('elevated_external_pressure_project_count', 0)}."
        ),
    ]

    return {
        "headline": headline,
        "bullets": bullets,
        "notes": f"Reporting period: {reporting_period_label}",
    }