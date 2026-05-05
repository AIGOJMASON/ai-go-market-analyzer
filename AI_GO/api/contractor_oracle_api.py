"""
Oracle API surface for contractor_builder_v1 (governed).
"""

from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from AI_GO.child_cores.contractor_builder_v1.oracle.market_snapshot_registry import (
    list_registered_snapshots,
)
from AI_GO.child_cores.contractor_builder_v1.oracle.oracle_service import (
    run_oracle_projection_governed,
)

router = APIRouter(prefix="/oracle", tags=["contractor_oracle"])


class OracleProjectionRequest(BaseModel):
    project_id: str
    snapshot_id: str
    exposure_profile_id: str
    domain_exposure: Dict[str, str]
    actor: str = "contractor_oracle_api"


@router.get("/snapshots")
def list_oracle_snapshots() -> dict:
    return {
        "status": "ok",
        "snapshots": list_registered_snapshots(),
    }


@router.post("/project-external-pressure")
def build_project_external_pressure(request: OracleProjectionRequest) -> dict:
    try:
        return run_oracle_projection_governed(request.model_dump())
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))