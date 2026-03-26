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


def _default_event_theme(sector: str) -> str:
    if sector == "energy":
        return "energy_rebound"
    if sector in {"utilities", "consumer_staples", "healthcare", "materials"}:
        return "necessity_rebound"
    return "market_move"


def _default_propagation(price_change: float) -> str:
    if abs(price_change) >= 3.0:
        return "fast"
    if abs(price_change) >= 1.5:
        return "moderate"
    return "limited"


def _default_confidence(price_change: float) -> str:
    if price_change >= 3.0:
        return "high"
    if price_change >= 1.5:
        return "medium"
    return "low"


def _normalize_event_signal(
    payload: Dict[str, Any],
    *,
    sector: str,
    confirmation: str,
    price_change: float,
) -> Dict[str, Any]:
    event_signal = payload.get("event_signal")
    if not isinstance(event_signal, dict):
        event_signal = {}

    if "event_theme" not in event_signal or not _safe_str(event_signal.get("event_theme")):
        event_signal["event_theme"] = _default_event_theme(sector)

    if "confirmed" not in event_signal:
        event_signal["confirmed"] = confirmation in {"confirmed", "partial"}

    if "propagation" not in event_signal or not _safe_str(event_signal.get("propagation")):
        event_signal["propagation"] = _default_propagation(price_change)

    return event_signal


def _normalize_candidates(
    payload: Dict[str, Any],
    *,
    symbol: str,
    sector: str,
    confirmation: str,
    price_change: float,
) -> list[Dict[str, Any]]:
    candidates = payload.get("candidates")

    if not isinstance(candidates, list) or not candidates:
        necessity_qualified = sector in {
            "energy",
            "utilities",
            "consumer_staples",
            "healthcare",
            "materials",
        }
        rebound_confirmed = confirmation in {"confirmed", "partial"}

        return [
            {
                "symbol": symbol,
                "sector": sector,
                "necessity_qualified": necessity_qualified,
                "rebound_confirmed": rebound_confirmed,
                "entry_signal": "reclaim support",
                "exit_signal": "short-term resistance",
                "confidence": _default_confidence(price_change),
            }
        ]

    normalized: list[Dict[str, Any]] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue

        candidate_symbol = _safe_str(candidate.get("symbol")) or symbol
        candidate_sector = (_safe_str(candidate.get("sector")) or sector).lower()
        candidate_confidence = _safe_str(candidate.get("confidence")) or _default_confidence(price_change)

        necessity_qualified = candidate.get("necessity_qualified")
        if necessity_qualified is None:
            necessity_qualified = candidate_sector in {
                "energy",
                "utilities",
                "consumer_staples",
                "healthcare",
                "materials",
            }

        rebound_confirmed = candidate.get("rebound_confirmed")
        if rebound_confirmed is None:
            rebound_confirmed = confirmation in {"confirmed", "partial"}

        normalized.append(
            {
                "symbol": candidate_symbol,
                "sector": candidate_sector,
                "necessity_qualified": bool(necessity_qualified),
                "rebound_confirmed": bool(rebound_confirmed),
                "entry_signal": _safe_str(candidate.get("entry_signal")) or "reclaim support",
                "exit_signal": _safe_str(candidate.get("exit_signal")) or "short-term resistance",
                "confidence": candidate_confidence,
            }
        )

    if normalized:
        return normalized

    return [
        {
            "symbol": symbol,
            "sector": sector,
            "necessity_qualified": sector in {
                "energy",
                "utilities",
                "consumer_staples",
                "healthcare",
                "materials",
            },
            "rebound_confirmed": confirmation in {"confirmed", "partial"},
            "entry_signal": "reclaim support",
            "exit_signal": "short-term resistance",
            "confidence": _default_confidence(price_change),
        }
    ]


def _normalize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    p = dict(payload)

    request_id = _safe_str(p.get("request_id")) or "live-request"
    sector = (_safe_str(p.get("sector")) or "").lower()
    confirmation = (_safe_str(p.get("confirmation")) or "").lower()
    price_change = _safe_float(p.get("price_change_pct"), 0.0)
    symbol = _safe_str(p.get("symbol")) or "UNKNOWN"

    if "case_id" not in p or not _safe_str(p.get("case_id")):
        p["case_id"] = request_id

    if "observed_at" not in p or not _safe_str(p.get("observed_at")):
        p["observed_at"] = datetime.utcnow().isoformat() + "Z"

    p["event_signal"] = _normalize_event_signal(
        p,
        sector=sector,
        confirmation=confirmation,
        price_change=price_change,
    )

    p["candidates"] = _normalize_candidates(
        p,
        symbol=symbol,
        sector=sector,
        confirmation=confirmation,
        price_change=price_change,
    )

    return p


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


@router.post(
    "/run/live",
    dependencies=[Depends(require_api_key), Depends(enforce_rate_limit)],
)
def run_market_analyzer_live(
    request: Request,
    request_payload: Dict[str, Any],
) -> Dict[str, Any]:
    return _execute_route(request, request_payload, route_mode="live_route")
