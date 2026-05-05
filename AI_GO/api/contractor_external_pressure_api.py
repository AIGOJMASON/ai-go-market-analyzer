from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from AI_GO.child_cores.contractor_builder_v1.adapters.root_handoff_adapter import (
    build_contractor_builder_input_from_root_handoff,
)


router = APIRouter(prefix="/external-pressure", tags=["contractor_external_pressure"])


class ContractorCuratedExternalPressureRequest(BaseModel):
    request_id: str = ""
    engine_handoff_packet: dict[str, Any] = Field(default_factory=dict)


def _extract_engine_handoff_packet(payload: dict[str, Any]) -> dict[str, Any]:
    candidate = payload.get("engine_handoff_packet")

    if candidate is None:
        candidate = payload.get("curated_child_core_handoff_packet")

    if candidate is None and payload.get("artifact_type") == "curated_child_core_handoff_packet":
        candidate = payload

    if not isinstance(candidate, dict):
        raise HTTPException(
            status_code=400,
            detail="Missing engine_handoff_packet or curated_child_core_handoff_packet",
        )

    if candidate.get("artifact_type") != "curated_child_core_handoff_packet":
        raise HTTPException(
            status_code=400,
            detail="Contractor external pressure route only accepts curated_child_core_handoff_packet",
        )

    if candidate.get("sealed") is not True:
        raise HTTPException(
            status_code=400,
            detail="Curated handoff packet must be sealed",
        )

    authority = candidate.get("authority", {})
    if not isinstance(authority, dict) or authority.get("authority_id") != "engines":
        raise HTTPException(
            status_code=400,
            detail="Curated handoff packet must come from engines authority",
        )

    if authority.get("curates_before_child_core") is not True:
        raise HTTPException(
            status_code=400,
            detail="Curated handoff packet is missing curates_before_child_core=true",
        )

    return candidate


@router.post("/curated")
def run_contractor_curated_external_pressure(
    request: ContractorCuratedExternalPressureRequest,
) -> dict[str, Any]:
    try:
        engine_handoff_packet = _extract_engine_handoff_packet(request.model_dump())

        contractor_input = build_contractor_builder_input_from_root_handoff(
            engine_handoff_packet
        )

        external_pressure_input = contractor_input.get("external_pressure_input", {})
        if not isinstance(external_pressure_input, dict):
            raise HTTPException(
                status_code=400,
                detail="Contractor handoff adapter did not emit external_pressure_input",
            )

        return {
            "status": "ok",
            "phase": "Phase 5A.4",
            "child_core_id": "contractor_builder_v1",
            "mode": "advisory",
            "approval_required": True,
            "execution_allowed": False,
            "mutation_allowed": False,
            "request_id": request.request_id,
            "route_mode": "curated_external_pressure",
            "contractor_input": contractor_input,
            "external_pressure_input": external_pressure_input,
            "authority": {
                "source_is_engine_curated": True,
                "research_core_required": True,
                "engines_required_before_child_core": True,
                "raw_provider_payload_allowed": False,
                "raw_research_packet_allowed": False,
                "provider_fetch_allowed": False,
                "workflow_mutation_allowed": False,
                "change_creation_allowed": False,
                "decision_creation_allowed": False,
                "execution_allowed": False,
            },
            "operator_guidance": {
                "summary": external_pressure_input.get("summary", ""),
                "recommended_use": "Review as external pressure context only.",
                "unsafe_use": (
                    "Do not mutate workflow, create changes, create decisions, "
                    "dispatch work, or execute contractor actions from this packet."
                ),
            },
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid contractor curated external pressure handoff: {type(exc).__name__}: {exc}",
        ) from exc