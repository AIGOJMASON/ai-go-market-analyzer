"""
Operator projection runtime for contractor_builder_v1.

This module assembles the final read-only contractor operator payload from bounded
project, portfolio, decision, change, compliance, and risk projections.

Projection is assembly only. It must not mutate truth or execute approvals.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Dict, List

from .project_projection import build_project_projection
from .portfolio_projection import build_portfolio_projection
from .decision_projection import build_decision_projection
from .change_projection import build_change_projection
from .compliance_projection import build_compliance_projection
from .risk_projection import build_risk_projection


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def build_contractor_operator_payload(
    *,
    request_id: str,
    project_profile: Dict[str, Any],
    baseline_lock: Dict[str, Any],
    workflow_snapshot: Dict[str, Any],
    latest_project_report: Dict[str, Any],
    portfolio_report: Dict[str, Any] | None = None,
    decision_records: List[Dict[str, Any]] | None = None,
    change_records: List[Dict[str, Any]] | None = None,
    compliance_snapshot: Dict[str, Any] | None = None,
    risk_records: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """
    Build the final contractor operator payload.
    """
    decision_records = decision_records or []
    change_records = change_records or []
    compliance_snapshot = compliance_snapshot or {}
    risk_records = risk_records or []

    project_panel = build_project_projection(
        project_profile=project_profile,
        baseline_lock=baseline_lock,
        workflow_snapshot=workflow_snapshot,
        latest_project_report=latest_project_report,
    )

    portfolio_panel = (
        build_portfolio_projection(portfolio_report=portfolio_report)
        if portfolio_report
        else {}
    )

    decisions_panel = build_decision_projection(decision_records=decision_records)
    changes_panel = build_change_projection(change_records=change_records)
    compliance_panel = build_compliance_projection(
        compliance_snapshot=compliance_snapshot
    )
    risks_panel = build_risk_projection(risk_records=risk_records)

    payload: Dict[str, Any] = {
        "generated_at": _utc_now_iso(),
        "request_id": request_id,
        "child_core_id": "contractor_builder_v1",
        "mode": "advisory",
        "approval_required": True,
        "execution_allowed": False,
        "project_panel": project_panel,
        "portfolio_panel": portfolio_panel,
        "decisions_panel": decisions_panel,
        "changes_panel": changes_panel,
        "compliance_panel": compliance_panel,
        "risks_panel": risks_panel,
        "summary_panel": {
            "project_id": project_profile.get("project_id", ""),
            "project_name": project_profile.get("project_name", ""),
            "current_phase_id": workflow_snapshot.get("current_phase_id", ""),
            "compliance_blocking": bool(compliance_snapshot.get("blocking", False)),
            "open_or_monitoring_risks": risks_panel.get("open_or_monitoring_count", 0),
            "approved_change_count": changes_panel.get("approved_change_count", 0),
            "customer_signoff_required_change_count": changes_panel.get(
                "customer_signoff_required_count",
                0,
            ),
            "blocking_unresolved_change_count": changes_panel.get(
                "blocking_unresolved_change_count",
                0,
            ),
            "change_blocking": bool(
                changes_panel.get("has_blocking_unresolved_changes", False)
            ),
        },
    }

    return payload