from __future__ import annotations

from typing import Any, Dict

from AI_GO.child_cores.contractor_builder_v1.report.report_executor import (
    execute_portfolio_weekly_report,
    execute_project_weekly_report,
    execute_report_approve,
    execute_report_archive,
)
from AI_GO.core.execution_gate.runtime_execution_gate import enforce_execution_gate
from AI_GO.core.governance.governed_context_builder import build_governed_context
from AI_GO.core.governance.governance_failure import raise_governance_failure
from AI_GO.core.state_runtime.contractor_state_profiles import validate_report_state
from AI_GO.core.watcher.contractor_watcher_profiles import watch_report


def _context(payload: Dict[str, Any], action: str) -> Dict[str, Any]:
    report = payload.get("report") if isinstance(payload.get("report"), dict) else {}

    state = validate_report_state(
        action=action,
        request=payload,
        report=report,
    )

    watcher = watch_report(
        action=action,
        request=payload,
        report=report,
    )

    context = build_governed_context(
        profile="contractor_report",
        action=action,
        route="/contractor-builder/report",
        request=payload,
        state=state,
        watcher=watcher,
    )

    if not state.get("valid"):
        raise_governance_failure(
            error="report_state_validation_failed",
            message="Report state validation failed",
            context=context,
        )

    if not watcher.get("valid"):
        raise_governance_failure(
            error="report_watcher_validation_failed",
            message="Report watcher validation failed",
            context=context,
        )

    return context


def project_weekly_report(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = _context(payload, "report_project_weekly")

    enforce_execution_gate(context["execution_gate"])

    result = execute_project_weekly_report(context)

    return {
        "mode": "governed_execution",
        **context,
        **result,
    }


def portfolio_weekly_report(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = _context(payload, "report_portfolio_weekly")

    enforce_execution_gate(context["execution_gate"])

    result = execute_portfolio_weekly_report(context)

    return {
        "mode": "governed_execution",
        **context,
        **result,
    }


def approve_report(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = _context(payload, "report_approve")

    enforce_execution_gate(context["execution_gate"])

    result = execute_report_approve(context)

    return {
        "mode": "governed_execution",
        **context,
        **result,
    }


def archive_report(payload: Dict[str, Any]) -> Dict[str, Any]:
    context = _context(payload, "report_archive")

    enforce_execution_gate(context["execution_gate"])

    result = execute_report_archive(context)

    return {
        "mode": "governed_execution",
        **context,
        **result,
    }