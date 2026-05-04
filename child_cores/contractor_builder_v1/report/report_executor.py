from __future__ import annotations

from typing import Any, Dict

from AI_GO.child_cores.contractor_builder_v1.report.approval_runtime import (
    apply_report_pm_approval,
    can_approve_report,
    can_archive_report,
    transition_report_status,
)
from AI_GO.child_cores.contractor_builder_v1.report.portfolio_weekly_builder import (
    build_portfolio_weekly_report,
)
from AI_GO.child_cores.contractor_builder_v1.report.project_weekly_builder import (
    build_project_weekly_report,
)
from AI_GO.child_cores.contractor_builder_v1.report.report_receipt_builder import (
    build_report_receipt,
    write_report_receipt,
)


def execute_project_weekly_report(context: Dict[str, Any]) -> Dict[str, Any]:
    request = dict(context["request"])

    report = build_project_weekly_report(
        project_id=request["project_id"],
        reporting_period_label=request["reporting_period_label"],
        workflow_snapshot=request.get("workflow_snapshot", {}),
        change_records=request.get("change_records", []),
        compliance_snapshot=request.get("compliance_snapshot", {}),
        router_snapshot=request.get("router_snapshot", {}),
        oracle_snapshot=request.get("oracle_snapshot", {}),
        decision_records=request.get("decision_records", []),
        risk_records=request.get("risk_records", []),
        assumption_records=request.get("assumption_records", []),
    )

    receipt = build_report_receipt(
        event_type="generate_project_weekly",
        subject_id=request["project_id"],
        report_id=report["report_id"],
        artifact_path=f"runtime://report/project/{report['report_id']}",
        actor=str(request.get("actor", "report_executor")),
    )
    receipt_path = write_report_receipt(receipt)

    return {
        "status": "generated",
        "report": report,
        "receipt_path": str(receipt_path),
    }


def execute_portfolio_weekly_report(context: Dict[str, Any]) -> Dict[str, Any]:
    request = dict(context["request"])

    report = build_portfolio_weekly_report(
        portfolio_id=request["portfolio_id"],
        reporting_period_label=request["reporting_period_label"],
        project_reports=request.get("project_reports", []),
    )

    receipt = build_report_receipt(
        event_type="generate_portfolio_weekly",
        subject_id=request["portfolio_id"],
        report_id=report["report_id"],
        artifact_path=f"runtime://report/portfolio/{report['report_id']}",
        actor=str(request.get("actor", "report_executor")),
    )
    receipt_path = write_report_receipt(receipt)

    return {
        "status": "generated",
        "report": report,
        "receipt_path": str(receipt_path),
    }


def execute_report_approve(context: Dict[str, Any]) -> Dict[str, Any]:
    request = dict(context["request"])
    report = dict(request["report"])

    if not can_approve_report(report):
        raise ValueError("Report not ready for approval")

    approved = apply_report_pm_approval(
        report,
        approved_by=request["approved_by"],
        signature=request["signature"],
        approval_notes=request.get("approval_notes", ""),
    )
    approved = transition_report_status(approved, new_status="approved")

    receipt = build_report_receipt(
        event_type="approve_report",
        subject_id=approved["subject_id"],
        report_id=approved["report_id"],
        artifact_path=f"runtime://report/approved/{approved['report_id']}",
        actor=str(request.get("actor", "report_executor")),
    )
    receipt_path = write_report_receipt(receipt)

    return {
        "status": "approved",
        "report": approved,
        "receipt_path": str(receipt_path),
    }


def execute_report_archive(context: Dict[str, Any]) -> Dict[str, Any]:
    request = dict(context["request"])
    report = dict(request["report"])

    if not can_archive_report(report):
        raise ValueError("Report not ready for archive")

    archived = transition_report_status(report, new_status="archived")

    receipt = build_report_receipt(
        event_type="archive_report",
        subject_id=archived["subject_id"],
        report_id=archived["report_id"],
        artifact_path=f"runtime://report/archived/{archived['report_id']}",
        actor=str(request.get("actor", "report_executor")),
    )
    receipt_path = write_report_receipt(receipt)

    return {
        "status": "archived",
        "report": archived,
        "receipt_path": str(receipt_path),
    }