from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from AI_GO.child_cores.contractor_builder_v1.weekly_cycle.weekly_cycle_service import (
    run_governed_weekly_cycle,
)


router = APIRouter(prefix="/weekly-cycle", tags=["contractor_weekly_cycle"])


class WeeklyCycleRunRequest(BaseModel):
    reporting_period_label: str
    project_payloads: List[Dict[str, Any]]
    portfolio_project_map: Dict[str, List[str]] = Field(default_factory=dict)
    actor: str = "contractor_weekly_cycle_api"


@router.post("/run")
def run_contractor_weekly_cycle(request: WeeklyCycleRunRequest) -> dict:
    try:
        return run_governed_weekly_cycle(request.model_dump())
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))