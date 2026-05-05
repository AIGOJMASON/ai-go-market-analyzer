"""
Oracle API surface for contractor_builder_v1.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List

from AI_GO.child_cores.contractor_builder_v1.oracle.snapshot_publisher import (
    publish_market_snapshot,
)
from AI_GO.child_cores.contractor_builder_v1.oracle.shock_classifier import (
    classify_shock_record,
)
from AI_GO.child_cores.contractor_builder_v1.oracle.exposure_profile_runtime import (
    build_project_exposure_profile,
)
from AI_GO.child_cores.contractor_builder_v1.oracle.projection_engine import (
    build_oracle_projection,
)
from AI_GO.child_cores.contractor_builder_v1.oracle.risk_radar_runtime import (
    build_risk_radar,
)
from AI_GO.child_cores.contractor_builder_v1.oracle.procurement_advisory import (
    build_procurement_advisory,
)
from AI_GO.child_cores.contractor_builder_v1.oracle.oracle_receipt_builder import (
    build_oracle_receipt,
    write_oracle_receipt,
)

router = APIRouter(prefix="/oracle", tags=["contractor_oracle"])


class OracleProjectionRequest(BaseModel):
    project_id: str
    snapshot_id: str
    exposure_profile_id: str
    domain_exposure: Dict[str, str]


@router.get("/snapshots")
def list_oracle_snapshots() -> dict:
    from AI_GO.child_cores.contractor_builder_v1.oracle.market_snapshot_registry import (
        list_registered_snapshots,
    )
    return {
        "status": "ok",
        "snapshots": list_registered_snapshots(),
    }


@router.post("/project-external-pressure")
def build_project_external_pressure(request: OracleProjectionRequest) -> dict:
    try:
        snapshot = publish_market_snapshot(request.snapshot_id)
        shock = classify_shock_record(
            shock_id=f"shock-{request.project_id}-{request.snapshot_id}",
            snapshot=snapshot,
        )
        exposure_profile = build_project_exposure_profile(
            exposure_profile_id=request.exposure_profile_id,
            project_id=request.project_id,
            domain_exposure=request.domain_exposure,
        )
        projection = build_oracle_projection(
            projection_id=f"projection-{request.project_id}-{request.snapshot_id}",
            project_id=request.project_id,
            snapshot=snapshot,
            shock_record=shock,
            exposure_profile=exposure_profile,
        )
        radar = build_risk_radar(
            radar_id=f"radar-{request.project_id}",
            project_id=request.project_id,
            projections=[projection],
        )
        advisory = build_procurement_advisory(
            advisory_id=f"advisory-{request.project_id}-{snapshot['market_domain']}",
            project_id=request.project_id,
            projection=projection,
        )

        receipt = build_oracle_receipt(
            event_type="create_projection",
            project_id=request.project_id,
            artifact_path=f"runtime://oracle/{request.project_id}/{request.snapshot_id}",
            details={"market_domain": snapshot["market_domain"]},
        )

        return {
            "status": "ok",
            "snapshot": snapshot,
            "shock": shock,
            "exposure_profile": exposure_profile,
            "projection": projection,
            "risk_radar": radar,
            "procurement_advisory": advisory,
            "receipt": receipt,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))