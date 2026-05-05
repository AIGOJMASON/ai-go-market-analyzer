from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from AI_GO.child_cores.contractor_builder_v1.report.report_service import (
    approve_report,
    archive_report,
    portfolio_weekly_report,
    project_weekly_report,
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
    actor: str = "contractor_report_api"


class PortfolioReportRequest(BaseModel):
    portfolio_id: str
    reporting_period_label: str
    project_reports: List[Dict[str, Any]]
    actor: str = "contractor_report_api"


class ReportApproveRequest(BaseModel):
    report: Dict[str, Any]
    approved_by: str
    signature: str
    approval_notes: str = ""
    actor: str = "contractor_report_api"


class ReportArchiveRequest(BaseModel):
    report: Dict[str, Any]
    actor: str = "contractor_report_api"


@router.post("/project-weekly")
def generate_project_weekly_report(request: ProjectReportRequest) -> dict:
    try:
        return project_weekly_report(request.model_dump())
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/portfolio-weekly")
def generate_portfolio_weekly_report(request: PortfolioReportRequest) -> dict:
    try:
        return portfolio_weekly_report(request.model_dump())
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/approve")
def approve_report_route(request: ReportApproveRequest) -> dict:
    try:
        return approve_report(request.model_dump())
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/archive")
def archive_report_route(request: ReportArchiveRequest) -> dict:
    try:
        return archive_report(request.model_dump())
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))