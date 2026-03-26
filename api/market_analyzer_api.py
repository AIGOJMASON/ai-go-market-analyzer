from __future__ import annotations

import importlib
import traceback
from typing import Any, Callable, Dict

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

try:
    from AI_GO.api.auth import require_api_key
    from AI_GO.api.rate_limit import enforce_rate_limit
    from AI_GO.api.request_logging import append_request_log, build_base_log_payload
    from AI_GO.api.schemas.market_analyzer_request import MarketAnalyzerRequest
    from AI_GO.api.schemas.market_analyzer_response import build_market_analyzer_response
    from AI_GO.child_cores.market_analyzer_v1.ui.operator_dashboard_runner import (
        run_operator_dashboard,
    )
except ModuleNotFoundError:
    from api.auth import require_api_key
    from api.rate_limit import enforce_rate_limit
    from api.request_logging import append_request_log, build_base_log_payload
    from api.schemas.market_analyzer_request import MarketAnalyzerRequest
    from api.schemas.market_analyzer_response import build_market_analyzer_response
    from child_cores.market_analyzer_v1.ui.operator_dashboard_runner import (
        run_operator_dashboard,
    )

router = APIRouter(prefix="/market-analyzer", tags=["market-analyzer"])


def _safe_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _extract_case_id(payload: Dict[str, Any], response: Dict[str, Any] | None = None) -> str | None:
    if response:
        case_panel = response.get("case_panel")
        if isinstance(case_panel, dict):
            case_id = _safe_str(case_panel.get("case_id"))
            if case_id:
                return case_id

        case_id = _safe_str(response.get("case_id"))
        if case_id:
            return case_id

    return _safe_str(payload.get("case_id")) or _safe_str(payload.get("request_id"))


def _extract_receipt_id(response: Dict[str, Any]) -> str | None:
    governance_panel = response.get("governance_panel")
    if isinstance(governance_panel, dict):
        receipt_id = _safe_str(governance_panel.get("receipt_id"))
        if receipt_id:
            return receipt_id

    return _safe_str(response.get("receipt_id"))


def _build_log_payload(
    request: Request,
    request_payload: Dict[str, Any],
    *,
    route_mode: str | None,
    response_status: int,
    response: Dict[str, Any] | None = None,
    auth_status: str | None = None,
) -> Dict[str, Any]:
    return build_base_log_payload(
        request_id=_safe_str(request_payload.get("request_id")),
        case_id=_extract_case_id(request_payload, response),
        auth_status=auth_status or getattr(request.state, "auth_status", None),
        response_status=response_status,
        route_mode=route_mode,
        receipt_id=_extract_receipt_id(response) if response else None,
        client_ip=getattr(request.state, "client_ip", None),
        api_key_id=getattr(request.state, "api_key_id", None),
        rate_limit_bucket_id=getattr(request.state, "rate_limit_bucket_id", None),
        rate_limit_count=getattr(request.state, "rate_limit_count", None),
    )


def _log_success(request: Request, request_payload: Dict[str, Any], *, route_mode: str, response: Dict[str, Any]) -> None:
    payload = _build_log_payload(
        request,
        request_payload,
        route_mode=route_mode,
        response_status=status.HTTP_200_OK,
        response=response,
    )
    payload.update(
        {
            "path": request.url.path,
            "method": request.method,
            "operator_id": getattr(request.state, "operator_id", None),
            "status": "success",
        }
    )
    append_request_log("run_success", payload)


def _log_unexpected_failure(request: Request, request_payload: Dict[str, Any], *, route_mode: str | None, exc: Exception) -> None:
    payload = _build_log_payload(
        request,
        request_payload,
        route_mode=route_mode,
        response_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        response=None,
    )
    payload.update(
        {
            "path": request.url.path,
            "method": request.method,
            "operator_id": getattr(request.state, "operator_id", None),
            "status": "unexpected_failure",
            "error_type": exc.__class__.__name__,
            "error_message": str(exc),
        }
    )
    append_request_log("run_unexpected_failure", payload)


def _load_live_execution_callable() -> Callable[..., Any] | None:
    module_names = [
        "AI_GO.child_cores.market_analyzer_v1.ui.live_data_runner",
        "child_cores.market_analyzer_v1.ui.live_data_runner",
    ]
    candidate_names = [
        "run_live_payload",
        "run_live_case",
    ]

    for module_name in module_names:
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue

        for candidate_name in candidate_names:
            candidate = getattr(module, candidate_name, None)
            if callable(candidate):
                return candidate

    return None


def _execute_live_callable(live_callable: Callable[..., Any], request_payload: Dict[str, Any]) -> Dict[str, Any]:
    return live_callable(request_payload)


def _execute_route(request: Request, request_payload: Dict[str, Any], *, route_mode: str) -> Dict[str, Any]:
    try:
        live_callable = _load_live_execution_callable()
        if not live_callable:
            raise RuntimeError("No live callable found")

        response = _execute_live_callable(live_callable, request_payload)

        _log_success(request, request_payload, route_mode=route_mode, response=response)
        return response

    except Exception as exc:
        print("\n🔥 LIVE ROUTE ERROR TRACEBACK 🔥")
        traceback.print_exc()
        print("🔥 END TRACEBACK 🔥\n")

        _log_unexpected_failure(request, request_payload, route_mode=route_mode, exc=exc)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(exc)}",
        ) from exc


@router.post("/run/live", dependencies=[Depends(require_api_key), Depends(enforce_rate_limit)])
def run_market_analyzer_live(request: Request, request_payload: Dict[str, Any]) -> Dict[str, Any]:
    return _execute_route(request, request_payload, route_mode="live_route")
