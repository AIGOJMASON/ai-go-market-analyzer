"""
Operator explainer for contractor_builder_v1.

This module translates the structured contractor operator payload into bounded,
operator-readable explanation. It must not invent facts, numbers, or authority.
"""

from __future__ import annotations

from typing import Any, Dict, List


def _build_project_read(payload: Dict[str, Any]) -> str:
    project_panel = payload.get("project_panel", {})
    summary_panel = payload.get("summary_panel", {})

    project_name = str(project_panel.get("project_name", "")).strip()
    current_phase_id = str(summary_panel.get("current_phase_id", "")).strip()
    compliance_blocking = bool(summary_panel.get("compliance_blocking", False))
    approved_change_count = int(summary_panel.get("approved_change_count", 0))
    open_risk_count = int(summary_panel.get("open_or_monitoring_risks", 0))

    clauses: List[str] = []

    if project_name:
        clauses.append(f"{project_name} is the active project")
    else:
        clauses.append("The active project is loaded")

    if current_phase_id:
        clauses.append(f"current phase is {current_phase_id}")

    if compliance_blocking:
        clauses.append("compliance blocking is active")
    else:
        clauses.append("no active compliance block is shown")

    clauses.append(f"approved changes on record: {approved_change_count}")
    clauses.append(f"open or monitoring risks: {open_risk_count}")

    return ". ".join(clauses) + "."


def _build_change_read(payload: Dict[str, Any]) -> str:
    changes_panel = payload.get("changes_panel", {})
    approved_total = changes_panel.get("approved_change_total_amount", 0.0)
    pending_approval_count = int(changes_panel.get("pending_approval_count", 0))
    approved_change_count = int(changes_panel.get("approved_change_count", 0))

    return (
        f"Change posture shows {approved_change_count} approved changes, "
        f"{pending_approval_count} awaiting approval, and "
        f"approved change total amount of {approved_total}."
    )


def _build_compliance_read(payload: Dict[str, Any]) -> str:
    compliance_panel = payload.get("compliance_panel", {})
    blocking = bool(compliance_panel.get("blocking", False))
    blocking_count = int(compliance_panel.get("blocking_count", 0))
    permit_count = int(compliance_panel.get("permit_count", 0))
    inspection_count = int(compliance_panel.get("inspection_count", 0))

    if blocking:
        return (
            f"Compliance posture is blocked with {blocking_count} blocking items "
            f"across {permit_count} permits and {inspection_count} inspections."
        )

    return (
        f"Compliance posture is not currently blocked. "
        f"Tracked permits: {permit_count}. Tracked inspections: {inspection_count}."
    )


def _build_risk_read(payload: Dict[str, Any]) -> str:
    risks_panel = payload.get("risks_panel", {})
    risk_count = int(risks_panel.get("risk_count", 0))
    open_count = int(risks_panel.get("open_or_monitoring_count", 0))
    occurred_count = int(risks_panel.get("occurred_count", 0))

    return (
        f"Risk posture shows {risk_count} total risks, "
        f"{open_count} open or monitoring, and {occurred_count} occurred."
    )


def _build_portfolio_read(payload: Dict[str, Any]) -> str:
    portfolio_panel = payload.get("portfolio_panel", {})
    if not portfolio_panel:
        return "No portfolio report is attached to this payload."

    metrics = portfolio_panel.get("portfolio_metrics", {})
    project_count = int(metrics.get("project_count", 0))
    blocking_project_count = int(metrics.get("blocking_project_count", 0))
    total_conflict_count = int(metrics.get("total_conflict_count", 0))

    return (
        f"Portfolio view covers {project_count} projects, "
        f"with {blocking_project_count} blocking and "
        f"{total_conflict_count} total routing conflicts."
    )


def build_contractor_operator_explanation(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a bounded explanation block from the structured contractor operator payload.
    """
    return {
        "operator_read": _build_project_read(payload),
        "change_read": _build_change_read(payload),
        "compliance_read": _build_compliance_read(payload),
        "risk_read": _build_risk_read(payload),
        "portfolio_read": _build_portfolio_read(payload),
        "operator_should_notice": [
            "Compliance blocking should be treated as a stop condition for forward progress when active.",
            "Approved change totals and pending approvals should be reviewed together, not separately.",
            "Open and monitoring risks should be read alongside current phase and compliance posture.",
        ],
        "uncertainty_flags": [
            "Explanation is bounded to structured payload fields only.",
            "No execution authority is implied by this explanation layer.",
        ],
    }