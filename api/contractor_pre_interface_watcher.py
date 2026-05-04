"""
Pre-interface watcher for contractor_builder_v1.

This module validates the final contractor dashboard payload before exposure.
It is verification only. It must not mutate runtime truth or approvals.
"""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/pre-interface", tags=["contractor_pre_interface"])


class ContractorPreInterfaceRequest(BaseModel):
    payload: Dict[str, Any]


def _validate_payload(payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    required_top_level = [
        "generated_at",
        "request_id",
        "child_core_id",
        "mode",
        "approval_required",
        "execution_allowed",
        "summary_panel",
        "project_panel",
        "decisions_panel",
        "changes_panel",
        "compliance_panel",
        "risks_panel",
        "explanation_panel",
    ]
    for field in required_top_level:
        if field not in payload:
            errors.append(f"Missing required payload field: {field}")

    if payload.get("mode") != "advisory":
        errors.append("mode must remain advisory")

    if payload.get("execution_allowed") is not False:
        errors.append("execution_allowed must be false")

    if payload.get("approval_required") is not True:
        errors.append("approval_required must be true")

    summary_panel = payload.get("summary_panel", {})
    if not isinstance(summary_panel, dict):
        errors.append("summary_panel must be a mapping")

    compliance_panel = payload.get("compliance_panel", {})
    if not isinstance(compliance_panel, dict):
        errors.append("compliance_panel must be a mapping")

    explanation_panel = payload.get("explanation_panel", {})
    if not isinstance(explanation_panel, dict):
        errors.append("explanation_panel must be a mapping")

    return errors


@router.post("/validate")
def validate_pre_interface_payload(request: ContractorPreInterfaceRequest) -> dict:
    try:
        errors = _validate_payload(request.payload)
        return {
            "status": "ok" if not errors else "invalid",
            "valid": len(errors) == 0,
            "errors": errors,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))