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
# UTIL
# -----------------------------

def _safe_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# -----------------------------
# LOGGING
# -----------------------------

def _build_log_payload(
    request: Request,
    payload: Dict[str, Any],
    *,
    route_mode: str | None,
    status_code: int,
) -> Dict[str, Any]:
    return build_base_log_payload(
        request_id=_safe_str(payload.get("request_id")),
        case_id=_safe_str(payload.get("case_id")),
        receipt_id=None,
        auth_status=getattr(request.state, "auth_status", None),
        response_status=status_code,
        route_mode=route_mode,
        client_ip=getattr(request.state, "client_ip", None),
        api_key_id=getattr(request.state, "api_key_id", None),
    )


def _log_success(request: Request, payload: Dict[str, Any], *, route_mode: str) -> None:
    log = _build_log_payload(request, payload, route_mode=route_mode, status_code=200)
    log["status"] = "success"
    append_request_log("run_success", log)


def _log_failure(request: Request, payload: Dict[str, Any], *, route_mode: str, exc: Exception) -> None:
    log = _build_log_payload(request, payload, route_mode=route_mode, status_code=500)
    log.update(
        {
            "status": "failure",
            "error_type": exc.__class__.__name__,
            "error_message": str(exc),
        }
    )
    append_request_log("run_failure", log)


# -----------------------------
# NORMALIZATION
# -----------------------------

def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    p = dict(payload)

    request_id = _safe_str(p.get("request_id")) or "live-request"
    sector = (_safe_str(p.get("sector")) or "").lower()
    confirmation = (_safe_str(p.get("confirmation")) or "").lower()
    price_change = _safe_float(p.get("price_change_pct"), 0.0)
    symbol = _safe_str(p.get("symbol")) or "UNKNOWN"

    # case_id
    if "case_id" not in p or not _safe_str(p.get("case_id")):
        p["case_id"] = request_id

    # observed_at
    if "observed_at" not in p or not _safe_str(p.get("observed_at")):
        p["observed_at"] = datetime.utcnow().isoformat() + "Z"

    # event_signal
    if "event_signal" not in p or not isinstance(p.get("event_signal"), dict):
        if sector == "energy":
            event_theme = "energy_rebound"
        elif sector in {"utilities", "consumer_staples", "healthcare", "materials"}:
            event_theme = "necessity_rebound"
        else:
            event_theme = "market_move"

        confirmed = confirmation in {"confirmed", "partial"}

        if abs(price_change) >= 3.0:
            propagation = "fast"
        elif abs(price_change) >= 1.5:
            propagation = "moderate"
        else:
            propagation = "limited"

        p["event_signal"] = {
            "event_theme": event_theme,
            "confirmed": confirmed,
            "propagation": propagation,
        }
    else:
        event_signal = dict(p["event_signal"])
        if "event_theme" not in event_signal or not _safe_str(event_signal.get("event_theme")):
            if sector == "energy":
                event_signal["event_theme"] = "energy_rebound"
            elif sector in {"utilities", "consumer_staples", "healthcare", "materials"}:
                event_signal["event_theme"] = "necessity_rebound"
            else:
                event_signal["event_theme"] = "market_move"

        if "confirmed" not in event_signal:
            event_signal["confirmed"] = confirmation in {"confirmed", "partial"}

        if "propagation" not in event_signal or not _safe_str(event_signal.get("propagation")):
            if abs(price_change) >= 3.0:
                event_signal["propagation"] = "fast"
            elif abs(price_change) >= 1.5:
                event_signal["propagation"] = "moderate"
            else:
                event_signal["propagation"] = "limited"

        p["event_signal"] = event_signal

    # candidates
    if "candidates" not in p or not isinstance(p.get("candidates"), list) or not p.get("candidates"):
        necessity_qualified = sector in {
            "energy",
            "utilities",
            "consumer_staples",
            "healthcare",
            "materials",
        }
        rebound_confirmed = confirmation in {"confirmed", "partial"}

        if price_change >= 3.0:
            confidence = "high"
        elif price_change >= 1.5:
            confidence = "medium"
        else:
            confidence = "low"

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
# EXECUTION
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
    normalized_payload = _normalize_payload(payload)
    return live_callable(normalized_payload)


# -----------------------------
# ROUTE
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
# ENDPOINT
# -----------------------------

@router.post(
    "/run/live",
    dependencies=[Depends(require_api_key), Depends(enforce_rate_limit)],
)
def run_market_analyzer_live(
    request: Request,
    request_payload: Dict[str, Any],
) -> Dict[str, Any]:
    return _execute_route(request, request_payload, route_mode="live_route")
