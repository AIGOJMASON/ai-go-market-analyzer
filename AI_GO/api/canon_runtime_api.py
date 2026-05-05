from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from AI_GO.core.canon_runtime.canon_context_builder import (
    build_domain_context,
    build_full_canon_context,
    build_layer_context,
)
from AI_GO.core.canon_runtime.canon_enforcer import (
    CANON_ENFORCER_VERSION,
    enforce_canon_action_from_dict,
)
from AI_GO.core.canon_runtime.canon_indexer import build_canon_index
from AI_GO.core.canon_runtime.canon_validator import validate_canon_runtime


router = APIRouter(prefix="/canon-runtime", tags=["canon_runtime"])


class CanonEnforcementRequest(BaseModel):
    action_type: str = Field(..., min_length=1)
    action_class: str = Field(..., min_length=1)
    actor: str = "unknown"
    target: str = ""
    project_id: str = ""
    phase_id: str = ""
    route: str = ""
    payload: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)


@router.get("/health")
def canon_runtime_health() -> dict:
    return {
        "status": "ok",
        "mode": "enforcement_ready",
        "can_mutate_lib": False,
        "can_mutate_code": False,
        "canon_enforcer_version": CANON_ENFORCER_VERSION,
        "purpose": "Expose canon awareness and enforce one canonical pass/block decision shape.",
        "entrypoint": "enforce_canon_action_from_dict",
    }


@router.get("/index")
def canon_runtime_index() -> dict:
    return build_canon_index()


@router.get("/validate")
def canon_runtime_validate() -> dict:
    return validate_canon_runtime()


@router.post("/enforce")
def canon_runtime_enforce(request: CanonEnforcementRequest) -> dict:
    try:
        return enforce_canon_action_from_dict(request.model_dump())
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "canon_enforcement_failed",
                "message": str(exc),
            },
        )


@router.get("/context/domain/{domain}")
def canon_runtime_domain_context(domain: str) -> dict:
    try:
        return build_domain_context(domain)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/context/layer/{layer_name}")
def canon_runtime_layer_context(layer_name: str) -> dict:
    try:
        return build_layer_context(layer_name)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/context/full")
def canon_runtime_full_context(limit: int = 25) -> dict:
    try:
        safe_limit = max(1, min(int(limit), 100))
        return build_full_canon_context(limit=safe_limit)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))