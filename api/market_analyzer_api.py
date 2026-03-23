from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from api.auth import require_api_key
from api.rate_limit import enforce_rate_limit
from api.request_logging import append_request_log, build_request_log_entry
from api.schemas.market_analyzer_request import MarketAnalyzerRequest
from api.schemas.market_analyzer_response import (
    MarketAnalyzerResponse,
    build_market_analyzer_response,
)
from child_cores.market_analyzer_v1.ui.operator_dashboard_runner import (
    run_operator_dashboard,
)

router = APIRouter(
    prefix="/market-analyzer",
    tags=["market_analyzer"],
    dependencies=[Depends(require_api_key), Depends(enforce_rate_limit)],
)


@router.get("/health")
def market_analyzer_health() -> dict:
    entry = build_request_log_entry(
        endpoint="/market-analyzer/health",
        request_id=None,
        case_id=None,
        auth_status="passed",
        response_status=200,
        detail="health_check",
    )
    append_request_log(entry)

    return {
        "status": "ok",
        "service": "market_analyzer_api",
        "core_id": "market_analyzer_v1",
        "mode": "advisory",
        "execution_allowed": False,
        "auth_required": True,
        "rate_limited": True,
    }


@router.post("/run", response_model=MarketAnalyzerResponse)
def run_market_analyzer(request: MarketAnalyzerRequest) -> MarketAnalyzerResponse:
    endpoint = "/market-analyzer/run"

    try:
        result = run_operator_dashboard(case_id=request.case_id)
        dashboard = result["dashboard"]

        response = build_market_analyzer_response(
            dashboard=dashboard,
            request_id=request.request_id,
        )

        entry = build_request_log_entry(
            endpoint=endpoint,
            request_id=request.request_id,
            case_id=request.case_id,
            auth_status="passed",
            response_status=200,
            route_mode=dashboard.get("route_mode"),
            receipt_id=dashboard.get("governance_panel", {}).get("receipt_id"),
            detail="run_success",
        )
        append_request_log(entry)

        return response
    except KeyError as exc:
        entry = build_request_log_entry(
            endpoint=endpoint,
            request_id=request.request_id,
            case_id=request.case_id,
            auth_status="passed",
            response_status=404,
            detail=f"unknown_case_id: {request.case_id}",
        )
        append_request_log(entry)

        raise HTTPException(
            status_code=404,
            detail=f"Unknown case_id: {request.case_id}",
        ) from exc
    except Exception as exc:
        entry = build_request_log_entry(
            endpoint=endpoint,
            request_id=request.request_id,
            case_id=request.case_id,
            auth_status="passed",
            response_status=500,
            detail=f"market_analyzer_run_failed: {exc}",
        )
        append_request_log(entry)

        raise HTTPException(
            status_code=500,
            detail=f"market_analyzer_run_failed: {exc}",
        ) from exc


@router.post("/run/raw")
def run_market_analyzer_raw(request: MarketAnalyzerRequest) -> JSONResponse:
    endpoint = "/market-analyzer/run/raw"

    try:
        result = run_operator_dashboard(case_id=request.case_id)
        dashboard = result["dashboard"]

        entry = build_request_log_entry(
            endpoint=endpoint,
            request_id=request.request_id,
            case_id=request.case_id,
            auth_status="passed",
            response_status=200,
            route_mode=dashboard.get("route_mode"),
            receipt_id=dashboard.get("governance_panel", {}).get("receipt_id"),
            detail="raw_run_success",
        )
        append_request_log(entry)

        return JSONResponse(
            content={
                "status": "ok",
                "request_id": request.request_id,
                "core_id": "market_analyzer_v1",
                "mode": "advisory",
                "execution_allowed": False,
                "payload": dashboard,
            }
        )
    except KeyError as exc:
        entry = build_request_log_entry(
            endpoint=endpoint,
            request_id=request.request_id,
            case_id=request.case_id,
            auth_status="passed",
            response_status=404,
            detail=f"unknown_case_id: {request.case_id}",
        )
        append_request_log(entry)

        raise HTTPException(
            status_code=404,
            detail=f"Unknown case_id: {request.case_id}",
        ) from exc
    except Exception as exc:
        entry = build_request_log_entry(
            endpoint=endpoint,
            request_id=request.request_id,
            case_id=request.case_id,
            auth_status="passed",
            response_status=500,
            detail=f"market_analyzer_raw_run_failed: {exc}",
        )
        append_request_log(entry)

        raise HTTPException(
            status_code=500,
            detail=f"market_analyzer_raw_run_failed: {exc}",
        ) from exc
       
