"""
Pre-interface watcher for contractor_builder_v1.

This module validates the final contractor dashboard payload before exposure.
It is verification only. It must not mutate runtime truth or approvals.

Validation authority lives in:
AI_GO.child_cores.contractor_builder_v1.validation.pre_interface_contract
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel

from AI_GO.child_cores.contractor_builder_v1.validation.pre_interface_contract import (
    validate_contractor_dashboard_payload,
)

router = APIRouter(prefix="/pre-interface", tags=["contractor_pre_interface"])


class ContractorPreInterfaceRequest(BaseModel):
    payload: Dict[str, Any]


@router.post("/watch")
def watch_contractor_payload(request: ContractorPreInterfaceRequest) -> dict:
    """
    Validate contractor dashboard payload prior to exposure.
    """
    errors = validate_contractor_dashboard_payload(request.payload)

    return {
        "watcher_status": "passed" if not errors else "failed",
        "child_core_id": "contractor_builder_v1",
        "error_count": len(errors),
        "errors": errors,
        "advisory_only_confirmed": (
            request.payload.get("mode") == "advisory"
            and request.payload.get("execution_allowed") is False
        ),
    }