from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from AI_GO.core.governance.governance_explainer import explain_governance_packet
from AI_GO.core.governance.governance_packet_store import load_governance_packet


router = APIRouter(prefix="/ai-go", tags=["ai_go_governance"])


class GovernanceExplainRequest(BaseModel):
    governance_decision: Dict[str, Any] = Field(default_factory=dict)
    watcher: Dict[str, Any] = Field(default_factory=dict)
    state: Dict[str, Any] = Field(default_factory=dict)
    canon: Dict[str, Any] = Field(default_factory=dict)
    execution_gate: Dict[str, Any] = Field(default_factory=dict)
    execution_result: Dict[str, Any] = Field(default_factory=dict)


class GovernanceExplainByIdRequest(BaseModel):
    profile: str
    governance_packet_id: str
    execution_result: Dict[str, Any] = Field(default_factory=dict)


@router.post("/explain-governance")
def explain_governance(request: GovernanceExplainRequest) -> Dict[str, Any]:
    try:
        return explain_governance_packet(request.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/explain-governance/by-id")
def explain_governance_by_id(request: GovernanceExplainByIdRequest) -> Dict[str, Any]:
    try:
        packet = load_governance_packet(
            profile=request.profile,
            governance_packet_id=request.governance_packet_id,
        )

        explanation = explain_governance_packet(
            {
                "governance_decision": packet,
                "watcher": packet.get("watcher", {}),
                "state": packet.get("state", {}),
                "canon": packet.get("canon", {}),
                "execution_gate": packet.get("execution_gate", {}),
                "execution_result": request.execution_result,
            }
        )

        explanation["source_packet"] = {
            "profile": request.profile,
            "governance_packet_id": request.governance_packet_id,
            "loaded_from_path": packet.get("_loaded_from_path", ""),
            "payload_hash": packet.get("integrity", {}).get("payload_hash", ""),
        }

        return explanation

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "governance_packet_not_found",
                "message": str(exc),
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/governance-packet/{profile}/{governance_packet_id}")
def get_governance_packet(profile: str, governance_packet_id: str) -> Dict[str, Any]:
    try:
        packet = load_governance_packet(
            profile=profile,
            governance_packet_id=governance_packet_id,
        )

        return {
            "status": "ok",
            "mode": "observer_only",
            "execution_allowed": False,
            "profile": profile,
            "governance_packet_id": governance_packet_id,
            "packet": packet,
            "authority_boundary": {
                "can_read": True,
                "can_explain": True,
                "can_execute": False,
                "can_override_governance": False,
                "can_mutate_state": False,
            },
        }

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "governance_packet_not_found",
                "message": str(exc),
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))