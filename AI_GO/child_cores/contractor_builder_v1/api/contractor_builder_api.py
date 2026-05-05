"""
Root API router for contractor_builder_v1.

This module mounts the contractor family API surfaces under one canonical router.
"""

from __future__ import annotations

from fastapi import APIRouter

from .contractor_projects_api import router as contractor_projects_router
from .contractor_workflow_api import router as contractor_workflow_router
from .contractor_change_api import router as contractor_change_router
from .contractor_decision_api import router as contractor_decision_router
from .contractor_risk_api import router as contractor_risk_router
from .contractor_assumption_api import router as contractor_assumption_router
from .contractor_comply_api import router as contractor_comply_router
from .contractor_router_api import router as contractor_router_router
from .contractor_oracle_api import router as contractor_oracle_router
from .contractor_report_api import router as contractor_report_router
from .contractor_weekly_cycle_api import router as contractor_weekly_cycle_router
from .contractor_pre_interface_watcher import router as contractor_pre_interface_watcher_router

router = APIRouter(prefix="/contractor-builder", tags=["contractor_builder_v1"])

router.include_router(contractor_projects_router)
router.include_router(contractor_workflow_router)
router.include_router(contractor_change_router)
router.include_router(contractor_decision_router)
router.include_router(contractor_risk_router)
router.include_router(contractor_assumption_router)
router.include_router(contractor_comply_router)
router.include_router(contractor_router_router)
router.include_router(contractor_oracle_router)
router.include_router(contractor_report_router)
router.include_router(contractor_weekly_cycle_router)
router.include_router(contractor_pre_interface_watcher_router)


@router.get("/health")
def contractor_builder_health() -> dict:
    """
    Basic health surface for contractor_builder_v1 API mounting.
    """
    return {
        "child_core_id": "contractor_builder_v1",
        "status": "ok",
        "mode": "advisory",
        "approval_required": True,
        "execution_allowed": False,
    }