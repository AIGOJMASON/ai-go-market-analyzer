from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from AI_GO.core.root_spine_health import (
    build_root_spine_component_index,
    build_root_spine_health_packet,
    build_root_spine_route_index,
)


router = APIRouter(prefix="/root-spine", tags=["contractor_root_spine"])


@router.get("/health")
def get_root_spine_health(request: Request) -> dict[str, Any]:
    return build_root_spine_health_packet(app=request.app)


@router.get("/index")
def get_root_spine_index(request: Request) -> dict[str, Any]:
    return {
        "status": "ok",
        "phase": "Phase 5A.5",
        "mode": "read_only",
        "execution_allowed": False,
        "mutation_allowed": False,
        "component_index": build_root_spine_component_index(),
        "route_index": build_root_spine_route_index(request.app),
    }


@router.get("/components")
def get_root_spine_components() -> dict[str, Any]:
    return {
        "status": "ok",
        "phase": "Phase 5A.5",
        "mode": "read_only",
        "execution_allowed": False,
        "mutation_allowed": False,
        "component_index": build_root_spine_component_index(),
    }