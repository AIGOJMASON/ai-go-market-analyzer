from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from AI_GO.core.state_runtime.contractor_dashboard_read_context import (
    build_dashboard_read_context,
)
from AI_GO.child_cores.contractor_builder_v1.projection.latest_payload_state import (
    persist_latest_dashboard_payload,
)


router = APIRouter(prefix="/live-dashboard", tags=["contractor_live_dashboard"])


class ContractorLiveDashboardRequest(BaseModel):
    project_id: str
    persist_visibility: bool = False  # NORTHSTAR: explicit, default OFF


def _clean_required(value: Any, field_name: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail=f"{field_name} is required")
    return cleaned


@router.get("/health")
def contractor_live_dashboard_health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "mode": "visibility_surface",
        "execution_allowed": False,
        "mutation_allowed": False,
        "purpose": "Live dashboard with optional governed visibility persistence.",
    }


@router.post("/run")
def run_live_dashboard(request: ContractorLiveDashboardRequest) -> Dict[str, Any]:
    project_id = _clean_required(request.project_id, "project_id")

    try:
        dashboard = build_dashboard_read_context(
            project_id=project_id,
            persist_packet=False,  # always read-only here
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "live_dashboard_build_failed",
                "message": str(exc),
            },
        ) from exc

    persistence_result = None

    # --- NORTHSTAR CONTROLLED VISIBILITY PERSISTENCE ---
    if request.persist_visibility:
        try:
            persistence_result = persist_latest_dashboard_payload(
                project_id=project_id,
                payload=dashboard,
                source="live_dashboard_api",
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "visibility_persistence_failed",
                    "message": str(exc),
                },
            ) from exc

    return {
        "status": "ok",
        "mode": "visibility_surface",
        "execution_allowed": False,
        "mutation_allowed": False,
        "project_id": project_id,
        "persist_visibility": bool(request.persist_visibility),
        "dashboard": dashboard,
        "visibility_persistence": persistence_result,
    }