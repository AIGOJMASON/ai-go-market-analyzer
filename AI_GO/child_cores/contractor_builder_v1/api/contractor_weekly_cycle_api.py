"""
Weekly cycle API surface for contractor_builder_v1.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List

from AI_GO.child_cores.contractor_builder_v1.weekly_cycle.weekly_cycle_runner import (
    run_weekly_cycle,
)
from AI_GO.child_cores.contractor_builder_v1.weekly_cycle.weekly_cycle_receipt_builder import (
    build_weekly_cycle_receipt,
    write_weekly_cycle_receipt,
)

router = APIRouter(prefix="/weekly-cycle", tags=["contractor_weekly_cycle"])


class WeeklyCycleRunRequest(BaseModel):
    reporting_period_label: str
    project_payloads: List[Dict[str, Any]]
    portfolio_project_map: Dict[str, List[str]] = {}


@router.post("/run")
def run_contractor_weekly_cycle(request: WeeklyCycleRunRequest) -> dict:
    try:
        cycle_record = run_weekly_cycle(
            reporting_period_label=request.reporting_period_label,
            project_payloads=request.project_payloads,
            portfolio_project_map=request.portfolio_project_map,
        )

        receipt = build_weekly_cycle_receipt(
            event_type="run_weekly_cycle",
            cycle_id=cycle_record["cycle_id"],
            artifact_path="AI_GO/state/contractor_builder_v1/weekly_cycle/current/latest_weekly_cycle_response.json",
            details={
                "project_report_count": cycle_record["project_report_count"],
                "portfolio_report_count": cycle_record["portfolio_report_count"],
                "cycle_status": cycle_record["cycle_status"],
            },
        )
        receipt_path = write_weekly_cycle_receipt(receipt)

        return {
            "status": cycle_record["cycle_status"],
            "cycle_record": cycle_record,
            "receipt_path": str(receipt_path),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))