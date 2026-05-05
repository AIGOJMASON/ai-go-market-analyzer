"""
Report API surface for contractor_builder_v1.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List

from AI_GO.child_cores.contractor_builder_v1.report.project_weekly_builder import (
    build_project_weekly_report,
)
from AI_GO.child_cores.contractor_builder_v1.report.portfolio_weekly_builder import (
    build_portfolio_weekly_report,
)
from AI_GO.child_cores.contractor_builder_v1.report.approval_runtime import (
    apply_report_pm_approval,
    can_approve_report,
    can_archive_report,
    transition_report_status,
)
from AI_GO.child_cores.contractor_builder_v1.report.report_receipt_builder import (
    build_report_receipt,
    write_report_receipt,
)

router = APIRouter(prefix="/report", tags=["contractor_report"])


class ProjectReportRequest(BaseModel):
    project_id: str
    reporting_period_label: str
    workflow_snapshot: Dict[str, Any]
    change_records: List[Dict[str, Any]]
    compliance_snapshot: Dict[str, Any]
    router_snapshot: Dict[str, Any]
    oracle_snapshot: Dict[str, Any]
    decision_records: List[Dict[str, Any]]
    risk_records: List[Dict[str, Any]]
    assumption_records: List[Dict[str, Any]]


class PortfolioReportRequest(BaseModel):
    portfolio_id: str
    reporting_period_label: str
    project_reports: List[Dict[str, Any]]


class ReportApproveRequest(BaseModel):
    report: Dict[str, Any]
    approved_by: str
    signature: str
    approval_notes: str = ""


class ReportArchiveRequest(BaseModel):
    report: Dict[str, Any]


@router.post("/project-weekly")
def generate_project_weekly_report(request: ProjectReportRequest) -> dict:
    try:
        report = build_project_weekly_report(
            project_id=request.project_id,
            reporting_period_label=request.reporting_period_label,
            workflow_snapshot=request.workflow_snapshot,
            change_records=request.change_records,
            compliance_snapshot=request.compliance_snapshot,
            router_snapshot=request.router_snapshot,
            oracle_snapshot=request.oracle_snapshot,
            decision_records=request.decision_records,
            risk_records=request.risk_records,
            assumption_records=request.assumption_records,
        )
        receipt = build_report_receipt(
            event_type="generate_project_weekly",
            subject_id=request.project_id,
            report_id=report["report_id"],
            artifact_path=f"runtime://report/project/{report['report_id']}",
        )
        receipt_path = write_report_receipt(receipt)

        return {
            "status": "generated",
            "report": report,
            "receipt_path": str(receipt_path),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/portfolio-weekly")
def generate_portfolio_weekly_report(request: PortfolioReportRequest) -> dict:
    try:
        report = build_portfolio_weekly_report(
            portfolio_id=request.portfolio_id,
            reporting_period_label=request.reporting_period_label,
            project_reports=request.project_reports,
        )
        receipt = build_report_receipt(
            event_type="generate_portfolio_weekly",
            subject_id=request.portfolio_id,
            report_id=report["report_id"],
            artifact_path=f"runtime://report/portfolio/{report['report_id']}",
        )
        receipt_path = write_report_receipt(receipt)

        return {
            "status": "generated",
            "report": report,
            "receipt_path": str(receipt_path),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/approve")
def approve_report(request: ReportApproveRequest) -> dict:
    try:
        if not can_approve_report(request.report):
            raise HTTPException(status_code=400, detail="Report not ready for approval")

        approved = apply_report_pm_approval(
            request.report,
            approved_by=request.approved_by,
            signature=request.signature,
            approval_notes=request.approval_notes,
        )
        approved = transition_report_status(approved, new_status="approved")

        receipt = build_report_receipt(
            event_type="approve_report",
            subject_id=approved["subject_id"],
            report_id=approved["report_id"],
            artifact_path=f"runtime://report/approved/{approved['report_id']}",
        )
        receipt_path = write_report_receipt(receipt)

        return {
            "status": "approved",
            "report": approved,
            "receipt_path": str(receipt_path),
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/archive")
def archive_report(request: ReportArchiveRequest) -> dict:
    try:
        if not can_archive_report(request.report):
            raise HTTPException(status_code=400, detail="Report not ready for archive")

        archived = transition_report_status(request.report, new_status="archived")

        receipt = build_report_receipt(
            event_type="archive_report",
            subject_id=archived["subject_id"],
            report_id=archived["report_id"],
            artifact_path=f"runtime://report/archived/{archived['report_id']}",
        )
        receipt_path = write_report_receipt(receipt)

        return {
            "status": "archived",
            "report": archived,
            "receipt_path": str(receipt_path),
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))