"""
Deterministic block builder for contractor_builder_v1.

This module builds numbers-first structured report blocks.
No invented numbers are allowed here.
"""

from __future__ import annotations

from typing import Any, Dict, List


def _count_approved_changes(change_records: List[Dict[str, Any]]) -> int:
    return sum(1 for record in change_records if record.get("status") == "approved")


def _sum_approved_change_amount(change_records: List[Dict[str, Any]]) -> float:
    total = 0.0
    for record in change_records:
        if record.get("status") != "approved":
            continue
        total += float(
            record.get("deterministic_block", {})
            .get("cost_delta", {})
            .get("total_change_order_amount") or 0.0
        )
    return round(total, 2)


def _count_open_risks(risk_records: List[Dict[str, Any]]) -> int:
    return sum(
        1 for record in risk_records
        if str(record.get("status", "")).strip() in {"Open", "Monitoring"}
    )


def _count_invalidated_assumptions(assumption_records: List[Dict[str, Any]]) -> int:
    return sum(
        1 for record in assumption_records
        if record.get("validation_status") == "Invalidated"
    )


def build_project_deterministic_block(
    *,
    project_id: str,
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
    Build the numbers-first deterministic block for one project.
    """
    return {
        "project_id": project_id,
        "workflow": {
            "phase_count": int(workflow_snapshot.get("phase_count", 0)),
            "current_phase_id": workflow_snapshot.get("current_phase_id", ""),
            "workflow_status": workflow_snapshot.get("workflow_status", ""),
        },
        "change": {
            "change_count": len(change_records),
            "approved_change_count": _count_approved_changes(change_records),
            "approved_change_total_amount": _sum_approved_change_amount(change_records),
        },
        "compliance": {
            "blocking": bool(compliance_snapshot.get("blocking", False)),
            "blocking_count": int(compliance_snapshot.get("blocking_count", 0)),
        },
        "router": {
            "conflict_count": int(router_snapshot.get("conflict_count", 0)),
            "cascade_risk_label": router_snapshot.get("cascade_risk_label", "none"),
            "overloaded_resource_count": int(
                router_snapshot.get("overloaded_resource_count", 0)
            ),
        },
        "oracle": {
            "summary_label": oracle_snapshot.get("summary_label", ""),
            "high_domain_count": int(len(oracle_snapshot.get("high_domains", []))),
            "moderate_domain_count": int(len(oracle_snapshot.get("moderate_domains", []))),
        },
        "decision": {
            "decision_count": len(decision_records),
            "approved_decision_count": sum(
                1 for record in decision_records
                if record.get("decision_status") == "approved"
            ),
        },
        "risk": {
            "risk_count": len(risk_records),
            "open_or_monitoring_count": _count_open_risks(risk_records),
        },
        "assumption": {
            "assumption_count": len(assumption_records),
            "invalidated_count": _count_invalidated_assumptions(assumption_records),
        },
    }


def build_portfolio_deterministic_block(
    *,
    portfolio_id: str,
    project_reports: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Build a portfolio-level deterministic block by aggregating project reports.
    """
    project_count = len(project_reports)

    total_approved_change_amount = 0.0
    total_blocking_projects = 0
    total_conflicts = 0
    total_open_risks = 0
    elevated_external_pressure_projects = 0

    for report in project_reports:
        block = report.get("deterministic_block", {})
        total_approved_change_amount += float(
            block.get("change", {}).get("approved_change_total_amount") or 0.0
        )
        total_blocking_projects += 1 if block.get("compliance", {}).get("blocking") else 0
        total_conflicts += int(block.get("router", {}).get("conflict_count", 0))
        total_open_risks += int(block.get("risk", {}).get("open_or_monitoring_count", 0))
        elevated_external_pressure_projects += (
            1 if block.get("oracle", {}).get("summary_label") == "elevated_external_pressure" else 0
        )

    return {
        "portfolio_id": portfolio_id,
        "project_count": project_count,
        "approved_change_total_amount": round(total_approved_change_amount, 2),
        "blocking_project_count": total_blocking_projects,
        "total_conflict_count": total_conflicts,
        "total_open_or_monitoring_risks": total_open_risks,
        "elevated_external_pressure_project_count": elevated_external_pressure_projects,
    }