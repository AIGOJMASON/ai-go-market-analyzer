from __future__ import annotations

import importlib
import traceback
from datetime import datetime
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

def _build_log_payload(request: Request, payload: Dict[str, Any], *, route_mode: str | None, status_code: int):
    return build_base_log_payload(
        request_id=_safe_str(payload.get("request_id")),
        case_id=_safe_str(payload.get("case_id")),
        receipt_id=None,  # required by contract
        auth_status=getattr(request.state, "auth_status", None),
        response_status=status_code,
        route_mode=route_mode,
        client_ip=getattr(request.state, "client_ip", None),
        api_key_id=getattr(request.state, "api_key_id", None),
    )


def _log_success(request: Request, payload: Dict[str, Any], *, route_mode: str):
    log = _build_log_payload(request, payload, route_mode=route_mode, status_code=200)
    log["status"] = "success"
    append_request_log("run_success", log)


def _log_failure(request: Request, payload: Dict[str, Any], *, route_mode: str, exc: Exception):
    log = _build_log_payload(request, payload, route_mode=route_mode, status_code=500)
    log.update({
        "status": "failure",
        "error_type": exc.__class__.__name__,
        "error_message": str(exc),
    })
    append_request_log("run_failure", log)


# -----------------------------
# PAYLOAD NORMALIZATION
# -----------------------------

def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert UI payload → canonical adapter payload
    """
    p = dict(payload)

    # case_id
    if "case_id" not in p:
        p["case_id"] = p.get("request_id")

    # observed_at
    if "observed_at" not in p:
        p["observed_at"] = datetime.utcnow().isoformat() + "Z"

    # event_signal
    if "event_signal" not in p:
        sector = (_safe_str(p.get("sector")) or "").lower()
        confirmation = (_safe_str(p.get("confirmation")) or "").lower()

        if sector == "energy" and confirmation == "confirmed":
            p["event_signal"] = "energy_rebound"
        elif confirmation == "confirmed":
            p["event_signal"] = "confirmed_move"
        else:
            p["event_signal"] = "speculative_move"

    # candidates
    if "candidates" not in p:
        symbol = _safe_str(p.get("symbol")) or "UNKNOWN"
        sector = (_safe_str(p.get("sector")) or "").lower()
        confirmation = (_safe_str(p.get("confirmation")) or "").lower()
        price_change = p.get("price_change_pct") or 0

        necessity_qualified = sector in [
            "energy",
            "utilities",
            "consumer_staples",
            "healthcare",
            "materials",
        ]

        rebound_confirmed = confirmation in ["confirmed", "partial"]

        if isinstance(price_change, (int, float)):
            if price_change >= 3:
                confidence = "high"
            elif price_change >= 1.5:
                confidence = "medium"
            else:
                confidence = "low"
        else:
            confidence = "unknown"

        p["candidates"] = [
            {
                "symbol": symbol,
                "necessity_qualified": necessity_qualified,
                "rebound_confirmed": rebound_confirmed,
                "entry_signal": "reclaim support",
                "exit_signal": "short-term resistance",
                "confidence": confidence,
            }
        ]

    return p


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


def _execute_live_callable(live_callable: Callable[..., Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = _normalize_payload(payload)
    return live_callable(payload)


# -----------------------------
# ROUTE EXECUTION
# -----------------------------

def _execute_route(request: Request, payload: Dict[str, Any], *, route_mode: str) -> Dict[str, Any]:
    try:
        live_callable = _load_live_callable()

        response = _execute_live_callable(live_callable, payload)

        _log_success(request, payload, route_mode=route_mode)

        return response

    except Exception as exc:
        print("\n🔥 LIVE ROUTE ERROR TRACEBACK 🔥")
        traceback.print_exc()
        print("🔥 END TRACEBACK 🔥\n")

        _log_failure(request, payload, route_mode=route_mode, exc=exc)

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
def run_market_analyzer_live(request: Request, request_payload: Dict[str, Any]) -> Dict[str, Any]:
    return _execute_route(
        request,
        request_payload,
        route_mode="live_route",
    )
