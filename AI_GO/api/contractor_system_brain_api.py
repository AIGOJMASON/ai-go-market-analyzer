from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query

from AI_GO.core.awareness.operator_system_brain_surface import (
    build_operator_system_brain_surface,
)


router = APIRouter(prefix="/system-brain", tags=["contractor_system_brain"])


@router.get("/surface")
def get_operator_system_brain_surface(
    limit: int = Query(default=500, ge=1, le=1000),
) -> Dict[str, Any]:
    try:
        surface = build_operator_system_brain_surface(limit=limit)

        return {
            "status": "ok",
            "mode": "read_only",
            "execution_allowed": False,
            "mutation_allowed": False,
            "surface": surface,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/summary")
def get_operator_system_brain_summary(
    limit: int = Query(default=500, ge=1, le=1000),
) -> Dict[str, Any]:
    try:
        surface = build_operator_system_brain_surface(limit=limit)

        return {
            "status": "ok",
            "mode": "read_only",
            "execution_allowed": False,
            "mutation_allowed": False,
            "plain_summary": surface.get("plain_summary", ""),
            "operator_cards": surface.get("operator_cards", []),
            "what_to_watch": surface.get("what_to_watch", []),
            "system_brain": surface.get("system_brain", {}),
            "authority": surface.get("authority", {}),
            "use_policy": surface.get("use_policy", {}),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))