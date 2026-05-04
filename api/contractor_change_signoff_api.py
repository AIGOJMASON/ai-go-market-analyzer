from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from AI_GO.child_cores.contractor_builder_v1.change.change_signoff_service import (
    complete_change_signoff,
    decline_change_signoff,
    send_change_signoff,
)


router = APIRouter(prefix="/change-signoff", tags=["contractor_change_signoff"])


class ChangeSignoffSendRequest(BaseModel):
    project_id: str
    change_packet_id: str
    client_name: str = "Customer"
    client_email: str
    actor: str = "contractor_change_signoff_api"
    allow_resend_if_sent: bool = True


class ChangeSignoffActionRequest(BaseModel):
    project_id: str
    change_packet_id: str
    actor: str = "contractor_change_signoff_api"


@router.post("/send")
def send_change_signoff_route(request: ChangeSignoffSendRequest) -> Dict[str, Any]:
    try:
        return send_change_signoff(request.model_dump())
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/complete")
def complete_change_signoff_route(request: ChangeSignoffActionRequest) -> Dict[str, Any]:
    try:
        return complete_change_signoff(request.model_dump())
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/decline")
def decline_change_signoff_route(request: ChangeSignoffActionRequest) -> Dict[str, Any]:
    try:
        return decline_change_signoff(request.model_dump())
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))