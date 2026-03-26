from __future__ import annotations

import importlib
import traceback
from typing import Any, Callable, Dict

from fastapi import APIRouter, Depends, HTTPException, Request, status

try:
    from AI_GO.api.auth import require_api_key
    from AI_GO.api.rate_limit import enforce_rate_limit
    from AI_GO.api.request_logging import append_request_log, build_base_log_payload
except ModuleNotFoundError:
    from api.auth import require_api_key
    from api.rate_limit import enforce_rate_limit
    from api.request_logging import append_request_log, build_base_log_payload

router = APIRouter(prefix="/market-analyzer", tags=["market-analyzer"])


# -----------------------------
# UTILITIES
# -----------------------------

def _safe_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


# -----------------------------
# LOGGING
# -----------------------------

def _build_log_payload(
    request: Request,
    request_payload: Dict[str, Any],
    *,
    route_mode: str | None,
    response_status: int,
) -> Dict[str, Any]:
    return build_base_log_payload(
        request_id=_safe_str(request_payload.get("request_id")),
        case_id=_safe_str(request_payload.get("case_id")) or _safe_str(request_payload.get("request_id")),
        auth_status=getattr(request.state, "auth_status", None),
        response_status=response_status,
        route_mode=route_mode,
        client_ip=getattr(request.state, "client_ip", None),
        api_key_id=getattr(request.state, "api_key_id", None),
    )


def _log_success(request: Request, payload: Dict[str, Any], *, route_mode: str) -> None:
    log = _build_log_payload(
        request,
        payload,
        route_mode=route_mode,
        response_status=status.HTTP_200_OK,
    )
    log["status"] = "success"
    append_request_log("run_success", log)


def _log_failure(request: Request, payload: Dict[str, Any], *, route_mode: str, exc: Exception) -> None:
    log = _build_log_payload(
        request,
        payload,
        route_mode=route_mode,
        response_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    log.update(
        {
            "status": "failure",
            "error_type": exc.__class__.__name__,
            "error_message": str(exc),
        }
    )
    append_request_log("run_failure", log)


# -----------------------------
# LIVE EXECUTION
# -----------------------------

def _load_live_callable() -> Callable[..., Any]:
    module_names = [
        "AI_GO.child_cores.market_analyzer_v1.ui.live_data_runner",
        "child_cores.market_analyzer_v1.ui.live_data_runner",
    ]

    for module_name in module_names:
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue

        for fn_name in ["run_live_payload", "run_live_case"]:
            fn = getattr(module, fn_name, None)
            if callable(fn):
                return fn

    raise RuntimeError("No live execution callable found")


def _execute_live_callable(live_callable: Callable[..., Any], request_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    🔥 CRITICAL FIX:
    Ensure case_id exists before hitting canonical adapter
    """

    if "case_id" not in request_payload:
        request_payload = dict(request_payload)
        request_payload["case_id"] = request_payload.get("request_id")

    return live_callable(request_payload)


# -----------------------------
# ROUTE
# -----------------------------

def _execute_route(request: Request, request_payload: Dict[str, Any], *, route_mode: str) -> Dict[str, Any]:
    try:
        live_callable = _load_live_callable()

        response = _execute_live_callable(live_callable, request_payload)

        _log_success(request, request_payload, route_mode=route_mode)

        return response

    except Exception as exc:
        print("\n🔥 LIVE ROUTE ERROR TRACEBACK 🔥")
        traceback.print_exc()
        print("🔥 END TRACEBACK 🔥\n")

        _log_failure(request, request_payload, route_mode=route_mode, exc=exc)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(exc)}",
        ) from exc


# -----------------------------
# API ENDPOINT
# -----------------------------

@router.post(
    "/run/live",
    dependencies=[Depends(require_api_key), Depends(enforce_rate_limit)],
)
def run_market_analyzer_live(
    request: Request,
    request_payload: Dict[str, Any],
) -> Dict[str, Any]:
    return _execute_route(
        request,
        request_payload,
        route_mode="live_route",
    )
