from __future__ import annotations

import traceback
import uuid
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request, status

try:
    from AI_GO.api.auth import require_api_key
    from AI_GO.api.request_logging import log_request_event
    from AI_GO.api.rate_limit import enforce_rate_limit
    from AI_GO.child_cores.market_analyzer_v1.ui.operator_dashboard_runner import run_operator_dashboard
except ModuleNotFoundError:
    from api.auth import require_api_key
    from api.request_logging import log_request_event
    from api.rate_limit import enforce_rate_limit
    from child_cores.market_analyzer_v1.ui.operator_dashboard_runner import run_operator_dashboard


router = APIRouter(prefix="/market-analyzer", tags=["market-analyzer"])


def _client_host(request: Request) -> str | None:
    return request.client.host if request.client else None


def _ensure_request_id(payload: Dict[str, Any]) -> str:
    rid = payload.get("request_id")
    if rid and isinstance(rid, str):
        return rid
    return f"auto-{uuid.uuid4().hex[:12]}"


def _basic_validate(payload: Dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Payload must be a JSON object")

    required_fields = ["symbol", "headline"]

    for field in required_fields:
        if not payload.get(field):
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}",
            )


def _execute(
    *,
    payload: Dict[str, Any],
    request: Request,
    operator_id: str,
    event_type_success: str,
    event_type_failure: str,
) -> Dict[str, Any]:

    request_id = _ensure_request_id(payload)
    payload["request_id"] = request_id

    _basic_validate(payload)

    try:
        result = run_operator_dashboard(payload)

        log_request_event(
            event_type=event_type_success,
            route=str(request.url.path),
            method=request.method,
            status_code=status.HTTP_200_OK,
            operator_id=operator_id,
            client_host=_client_host(request),
            request_id=result.get("request_id") or request_id,
            route_mode=result.get("route_mode"),
            outcome="success",
        )

        return result

    except HTTPException:
        raise

    except Exception:
        traceback.print_exc()

        log_request_event(
            event_type=event_type_failure,
            route=str(request.url.path),
            method=request.method,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            operator_id=operator_id,
            client_host=_client_host(request),
            request_id=request_id,
            outcome="internal_error",
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/run")
async def run_market_analyzer(
    payload: Dict[str, Any],
    request: Request,
    operator_id: str = Depends(require_api_key),
    _: None = Depends(enforce_rate_limit),
) -> Dict[str, Any]:
    return _execute(
        payload=payload,
        request=request,
        operator_id=operator_id,
        event_type_success="market_analyzer_run",
        event_type_failure="market_analyzer_run_failed",
    )


@router.post("/run/live")
async def run_market_analyzer_live(
    payload: Dict[str, Any],
    request: Request,
    operator_id: str = Depends(require_api_key),
    _: None = Depends(enforce_rate_limit),
) -> Dict[str, Any]:
    return _execute(
        payload=payload,
        request=request,
        operator_id=operator_id,
        event_type_success="market_analyzer_live_run",
        event_type_failure="market_analyzer_live_run_failed",
    )