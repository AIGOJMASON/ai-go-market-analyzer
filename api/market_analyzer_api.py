from __future__ import annotations

import importlib
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


def _log_success(
    request: Request,
    request_payload: Dict[str, Any],
    *,
    route_mode: str,
    response: Dict[str, Any],
    event_type: str = "run_success",
) -> None:
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
    append_request_log(event_type, payload)


def _log_http_failure(
    request: Request,
    request_payload: Dict[str, Any],
    *,
    route_mode: str | None,
    exc: HTTPException,
    event_type: str = "run_http_failure",
) -> None:
    payload = _build_log_payload(
        request,
        request_payload,
        route_mode=route_mode,
        response_status=exc.status_code,
        response=None,
    )
    payload.update(
        {
            "path": request.url.path,
            "method": request.method,
            "operator_id": getattr(request.state, "operator_id", None),
            "status": "http_failure",
            "error_detail": exc.detail,
        }
    )
    append_request_log(event_type, payload)


def _log_unexpected_failure(
    request: Request,
    request_payload: Dict[str, Any],
    *,
    route_mode: str | None,
    exc: Exception,
    event_type: str = "run_unexpected_failure",
) -> None:
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
    append_request_log(event_type, payload)


def _invoke_operator_dashboard(case_id: str) -> Dict[str, Any]:
    result = run_operator_dashboard(case_id=case_id)

    if hasattr(result, "model_dump"):
        result = result.model_dump(by_alias=True, exclude_none=False)

    if not isinstance(result, dict):
        raise RuntimeError("operator dashboard runner returned unsupported result type")

    if isinstance(result.get("dashboard"), dict):
        return result["dashboard"]

    if isinstance(result.get("payload"), dict):
        return result["payload"]

    return result


def _normalize_runtime_result(result: Any) -> Dict[str, Any]:
    if hasattr(result, "model_dump"):
        result = result.model_dump(by_alias=True, exclude_none=False)

    if not isinstance(result, dict):
        raise RuntimeError("live execution returned unsupported result type")

    if isinstance(result.get("dashboard"), dict):
        return result["dashboard"]

    if isinstance(result.get("payload"), dict):
        return result["payload"]

    return result


def _load_live_execution_callable() -> Callable[..., Any] | None:
    module_names = [
        "AI_GO.child_cores.market_analyzer_v1.ui.live_data_runner",
        "child_cores.market_analyzer_v1.ui.live_data_runner",
    ]
    candidate_names = [
        "run_live_payload",
        "run_live_input",
        "run_live_data",
        "run_live_route",
        "run_live_packet",
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
    call_patterns = [
        lambda fn, payload: fn(request_payload=payload),
        lambda fn, payload: fn(payload=payload),
        lambda fn, payload: fn(live_payload=payload),
        lambda fn, payload: fn(case=payload),
        lambda fn, payload: fn(packet=payload),
        lambda fn, payload: fn(payload),
    ]

    last_type_error: TypeError | None = None

    for call_pattern in call_patterns:
        try:
            result = call_pattern(live_callable, request_payload)
            return _normalize_runtime_result(result)
        except TypeError as exc:
            last_type_error = exc
            continue

    if last_type_error is not None:
        raise last_type_error

    raise RuntimeError("no valid live execution call pattern succeeded")


def _build_placeholder_response(
    request_payload: Dict[str, Any],
    *,
    route_mode: str,
    operator_id: str | None,
) -> Dict[str, Any]:
    governed_payload = dict(request_payload)
    governed_payload.setdefault("route_mode", route_mode)
    governed_payload.setdefault("mode", "advisory")
    governed_payload.setdefault("execution_allowed", False)

    if operator_id:
        governed_payload.setdefault("operator_id", operator_id)

    response = build_market_analyzer_response(governed_payload)
    return response.model_dump(by_alias=True, exclude_none=False)


def _build_fixture_response(request: Request, request_payload: Dict[str, Any]) -> Dict[str, Any]:
    case_id = _extract_case_id(request_payload)
    if case_id:
        return _invoke_operator_dashboard(case_id)

    return _build_placeholder_response(
        request_payload,
        route_mode="fixture_route",
        operator_id=getattr(request.state, "operator_id", None),
    )


def _build_live_response(request: Request, request_payload: Dict[str, Any]) -> Dict[str, Any]:
    case_id = _safe_str(request_payload.get("case_id"))
    if case_id:
        return _invoke_operator_dashboard(case_id)

    live_callable = _load_live_execution_callable()
    if live_callable is None:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=(
                "Live payload execution is not wired to a callable runtime surface. "
                "Provide case_id for dashboard-backed execution or wire a payload-based live runner."
            ),
        )

    return _execute_live_callable(live_callable, request_payload)


def _execute_route(
    request: Request,
    request_payload: Dict[str, Any],
    *,
    route_mode: str,
) -> Dict[str, Any]:
    try:
        if route_mode == "fixture_route":
            response = _build_fixture_response(request, request_payload)
        elif route_mode == "live_route":
            response = _build_live_response(request, request_payload)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported route_mode: {route_mode}",
            )

        _log_success(
            request,
            request_payload,
            route_mode=route_mode,
            response=response,
        )
        return response

    except HTTPException as exc:
        _log_http_failure(
            request,
            request_payload,
            route_mode=route_mode,
            exc=exc,
        )
        raise

    except Exception as exc:
        _log_unexpected_failure(
            request,
            request_payload,
            route_mode=route_mode,
            exc=exc,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error.",
        ) from exc


@router.post(
    "/run",
    dependencies=[Depends(require_api_key), Depends(enforce_rate_limit)],
)
def run_market_analyzer(
    request: Request,
    request_payload: Dict[str, Any],
) -> Dict[str, Any]:
    return _execute_route(
        request,
        request_payload,
        route_mode="fixture_route",
    )


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


@router.post(
    "/run/raw",
    dependencies=[Depends(require_api_key), Depends(enforce_rate_limit)],
)
def run_market_analyzer_raw(
    request: Request,
    raw_request: MarketAnalyzerRequest,
) -> JSONResponse:
    endpoint_payload = {
        "request_id": raw_request.request_id,
        "case_id": raw_request.case_id,
    }

    try:
        dashboard = _invoke_operator_dashboard(raw_request.case_id)

        _log_success(
            request,
            endpoint_payload,
            route_mode=dashboard.get("route_mode", "raw_route"),
            response=dashboard,
            event_type="raw_run_success",
        )

        return JSONResponse(
            content={
                "status": "ok",
                "request_id": raw_request.request_id,
                "core_id": "market_analyzer_v1",
                "mode": "advisory",
                "execution_allowed": False,
                "payload": dashboard,
            }
        )

    except KeyError as exc:
        http_exc = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown case_id: {raw_request.case_id}",
        )
        _log_http_failure(
            request,
            endpoint_payload,
            route_mode=None,
            exc=http_exc,
            event_type="raw_run_http_failure",
        )
        raise http_exc from exc

    except HTTPException as exc:
        _log_http_failure(
            request,
            endpoint_payload,
            route_mode=None,
            exc=exc,
            event_type="raw_run_http_failure",
        )
        raise

    except Exception as exc:
        _log_unexpected_failure(
            request,
            endpoint_payload,
            route_mode=None,
            exc=exc,
            event_type="raw_run_unexpected_failure",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"market_analyzer_raw_run_failed: {exc}",
        ) from exc
