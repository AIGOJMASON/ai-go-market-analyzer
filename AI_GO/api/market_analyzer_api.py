from __future__ import annotations

import json
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request, status

from AI_GO.api.auth import require_api_key
from AI_GO.api.closeout import create_closeout_artifact
from AI_GO.api.rate_limit import enforce_rate_limit
from AI_GO.api.receipt_watcher import (
    persist_validation_result,
    validate_market_analyzer_receipt,
)
from AI_GO.api.receipts import build_run_receipt, persist_receipt
from AI_GO.api.request_logging import log_request_event
from AI_GO.core.child_core_handoff.consumption_adapter import (
    build_child_core_consumption_packet,
)
from AI_GO.core.governance.governed_persistence import governed_write_json
from AI_GO.core.governance.route_enforcement import enforce_route_level_access
from AI_GO.core.strategy.pm_market_analyzer_route import route_market_analyzer_packet


router = APIRouter(prefix="/market-analyzer", tags=["market-analyzer"])


MARKET_ANALYZER_API_VERSION = "northstar_market_analyzer_api_v1"

MARKET_ANALYZER_SNAPSHOT_MUTATION_CLASS = "market_analyzer_snapshot_persistence"
MARKET_ANALYZER_SNAPSHOT_PERSISTENCE_TYPE = "filesystem"
MARKET_ANALYZER_SNAPSHOT_ADVISORY_ONLY = False


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _classification_block() -> Dict[str, Any]:
    return {
        "mutation_class": MARKET_ANALYZER_SNAPSHOT_MUTATION_CLASS,
        "persistence_type": MARKET_ANALYZER_SNAPSHOT_PERSISTENCE_TYPE,
        "advisory_only": MARKET_ANALYZER_SNAPSHOT_ADVISORY_ONLY,
        "execution_allowed": False,
        "state_mutation_allowed": False,
        "workflow_mutation_allowed": False,
        "project_truth_mutation_allowed": False,
        "authority_mutation_allowed": False,
    }


def _authority_block() -> Dict[str, Any]:
    return {
        "governed_persistence": True,
        "snapshot_only": True,
        "can_execute": False,
        "can_mutate_operational_state": False,
        "can_override_governance": False,
        "can_override_watcher": False,
        "can_override_execution_gate": False,
    }


def _resolve_project_root() -> Path:
    current = Path(__file__).resolve()

    for candidate in [current] + list(current.parents):
        if (candidate / "app.py").exists() and (candidate / "state").exists():
            return candidate

    for candidate in current.parents:
        if (candidate / "app.py").exists():
            return candidate

    return current.parents[1]


PROJECT_ROOT = _resolve_project_root()
OPERATOR_DASHBOARD_STATE_DIR = PROJECT_ROOT / "state" / "operator_dashboard"
BY_REQUEST_DIR = OPERATOR_DASHBOARD_STATE_DIR / "by_request"
LATEST_OPERATOR_PAYLOAD_PATH = OPERATOR_DASHBOARD_STATE_DIR / "latest_operator_payload.json"
LATEST_LIVE_OPERATOR_PAYLOAD_PATH = OPERATOR_DASHBOARD_STATE_DIR / "latest_live_operator_payload.json"


def _client_host(request: Request) -> str | None:
    return request.client.host if request.client else None


def _ensure_request_id(payload: Dict[str, Any]) -> str:
    request_id = payload.get("request_id")
    if isinstance(request_id, str) and request_id.strip():
        return request_id.strip()

    return f"auto-{uuid.uuid4().hex[:12]}"


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _safe_str(value: Any, default: str = "") -> str:
    cleaned = str(value or "").strip()
    return cleaned or default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _write_json(path: Path, payload: Dict[str, Any]) -> Path:
    payload.setdefault("classification", _classification_block())
    payload.setdefault("authority", _authority_block())

    return governed_write_json(
        path=path,
        payload=payload,
        mutation_class=MARKET_ANALYZER_SNAPSHOT_MUTATION_CLASS,
        persistence_type=MARKET_ANALYZER_SNAPSHOT_PERSISTENCE_TYPE,
        advisory_only=MARKET_ANALYZER_SNAPSHOT_ADVISORY_ONLY,
    )


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {
            "status": "empty",
            "mode": "read_only",
            "execution_allowed": False,
            "mutation_allowed": False,
            "path": str(path),
        }

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "status": "error",
            "mode": "read_only",
            "execution_allowed": False,
            "mutation_allowed": False,
            "path": str(path),
            "error": str(exc),
        }

    return payload if isinstance(payload, dict) else {}


def read_latest_operator_payload() -> Dict[str, Any]:
    return _read_json(LATEST_OPERATOR_PAYLOAD_PATH)


def persist_latest_operator_payload(payload: Dict[str, Any]) -> Path:
    return _write_json(LATEST_OPERATOR_PAYLOAD_PATH, payload)


def _persist_request_snapshot(
    *,
    final_payload: Dict[str, Any],
    latest_live: bool,
) -> None:
    request_id = _safe_str(final_payload.get("request_id"), default=f"auto-{uuid.uuid4().hex[:12]}")

    final_payload["request_id"] = request_id
    final_payload.setdefault("classification", _classification_block())
    final_payload.setdefault("authority", _authority_block())

    _write_json(BY_REQUEST_DIR / f"{request_id}.json", final_payload)
    persist_latest_operator_payload(final_payload)

    if latest_live:
        _write_json(LATEST_LIVE_OPERATOR_PAYLOAD_PATH, final_payload)


def _basic_validate(payload: Dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Payload must be a JSON object")


def _extract_curated_engine_handoff(payload: Dict[str, Any]) -> Dict[str, Any]:
    engine_handoff_packet = _safe_dict(payload.get("engine_handoff_packet"))

    if not engine_handoff_packet:
        raise HTTPException(
            status_code=400,
            detail="Curated live route requires engine_handoff_packet.",
        )

    source = _safe_dict(engine_handoff_packet.get("source"))
    authority = _safe_dict(engine_handoff_packet.get("authority"))
    target_child_cores = _safe_list(engine_handoff_packet.get("target_child_cores"))

    source_is_engine_curated = (
        engine_handoff_packet.get("artifact_type") in {
            "curated_child_core_handoff",
            "engine_curated_child_core_handoff",
            "curated_child_core_handoff_packet",
        }
        or authority.get("source_is_engine_curated") is True
        or engine_handoff_packet.get("engine_authority") is True
    )

    if not source_is_engine_curated:
        raise HTTPException(
            status_code=400,
            detail="Curated handoff packet must come from engines authority.",
        )

    if target_child_cores and "market_analyzer_v1" not in target_child_cores:
        raise HTTPException(
            status_code=400,
            detail="Curated handoff packet does not target market_analyzer_v1.",
        )

    if source.get("raw_provider_payload_allowed") is True:
        raise HTTPException(
            status_code=400,
            detail="Curated handoff may not allow raw provider payload.",
        )

    return engine_handoff_packet


def _build_live_input_from_engine_handoff(payload: Dict[str, Any]) -> Dict[str, Any]:
    engine_handoff_packet = _extract_curated_engine_handoff(payload)

    try:
        consumption_packet = build_child_core_consumption_packet(
            child_core_id="market_analyzer_v1",
            engine_handoff_packet=engine_handoff_packet,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Market Analyzer curated handoff: {type(exc).__name__}: {exc}",
        ) from exc

    curated = _safe_dict(consumption_packet.get("curated_input"))

    request_id = _safe_str(payload.get("request_id")) or _safe_str(
        consumption_packet.get("adapter_id"),
        default=f"curated-{uuid.uuid4().hex[:12]}",
    )

    return {
        "request_id": request_id,
        "symbol": _safe_str(curated.get("symbol")),
        "headline": _safe_str(curated.get("title") or curated.get("headline")),
        "summary": _safe_str(curated.get("summary")),
        "price": curated.get("price"),
        "price_change_pct": _safe_float(curated.get("price_change_pct"), 0.0),
        "sector": _safe_str(curated.get("sector"), default="unknown"),
        "confirmation": _safe_str(curated.get("confirmation"), default="partial"),
        "observed_at": _safe_str(curated.get("observed_at")),
        "source": "root_intelligence_spine",
        "source_refs": _safe_list(curated.get("source_refs")),
        "pre_weight": curated.get("pre_weight", 0),
        "trust_class": _safe_str(curated.get("trust_class")),
        "interpretation_class": _safe_str(curated.get("interpretation_class")),
        "curated_live_source": {
            "artifact_type": "market_analyzer_root_handoff_input",
            "source_consumption_adapter_id": consumption_packet.get("adapter_id"),
            "engine_handoff_artifact_type": engine_handoff_packet.get("artifact_type"),
            "research_packet_id": _safe_dict(engine_handoff_packet.get("source")).get(
                "research_packet_id"
            ),
            "source_is_engine_curated": True,
            "raw_provider_payload_allowed": False,
            "provider_fetch_allowed": False,
            "direct_live_post_allowed": False,
        },
    }


def _event_theme_from_payload(payload: Dict[str, Any]) -> str:
    explicit = _safe_str(payload.get("event_theme"))
    if explicit:
        return explicit

    headline = _safe_str(payload.get("headline") or payload.get("summary")).lower()

    if "energy" in headline or _safe_str(payload.get("sector")).lower() == "energy":
        return "energy_rebound"
    if "oil" in headline or "gas" in headline:
        return "energy_supply_shock"
    if "tech" in headline or "ai" in headline:
        return "tech_momentum"
    if "inflation" in headline:
        return "inflation_pressure"
    if "rate" in headline or "fed" in headline:
        return "rate_shift"

    return "unknown_event"


def _build_pm_packet(payload: Dict[str, Any]) -> Dict[str, Any]:
    request_id = _ensure_request_id(payload)
    symbol = _safe_str(payload.get("symbol"), default="UNKNOWN")
    headline = _safe_str(payload.get("headline") or payload.get("summary"), default="No headline")
    event_theme = _event_theme_from_payload(payload)
    confirmation = _safe_str(payload.get("confirmation"), default="partial").lower()

    confirmed = confirmation in {"confirmed", "strong", "validated", "high", "true"}

    if confirmation == "partial":
        confirmed = True

    price_change_pct = _safe_float(payload.get("price_change_pct"), 0.0)

    return {
        "packet_type": "pm_style_live_input",
        "case_id": request_id,
        "parent_authority": "PM_CORE",
        "target_core": "market_analyzer_v1",
        "event_context": {
            "theme": event_theme,
            "propagation": "curated",
            "confirmed": confirmed,
            "headline": headline,
            "macro_bias": _safe_str(payload.get("macro_bias"), default="neutral"),
        },
        "candidates": [
            {
                "symbol": symbol,
                "necessity_qualified": True,
                "rebound_confirmed": True,
                "entry_signal": "reclaim support",
                "exit_signal": "short-term resistance",
                "confidence": "medium",
                "price_change_pct": price_change_pct,
                "sector": _safe_str(payload.get("sector"), default="unknown"),
            }
        ],
    }


def _build_operator_payload(
    *,
    payload: Dict[str, Any],
    routed: Dict[str, Any],
) -> Dict[str, Any]:
    request_id = _ensure_request_id(payload)
    symbol = _safe_str(payload.get("symbol"), default="UNKNOWN")
    headline = _safe_str(payload.get("headline") or payload.get("summary"), default=symbol)
    event_theme = _event_theme_from_payload(payload)

    recommendation_packet = _safe_dict(routed.get("trade_recommendation_packet"))
    recommendations = _safe_list(recommendation_packet.get("recommendations"))

    final_payload: Dict[str, Any] = {
        "status": "ok" if routed.get("status") == "ok" else routed.get("status", "ok"),
        "api_version": MARKET_ANALYZER_API_VERSION,
        "request_id": request_id,
        "core_id": "market_analyzer_v1",
        "route_mode": "pm_route",
        "mode": "advisory",
        "execution_allowed": False,
        "approval_required": True,
        "mutation_allowed": False,
        "dashboard_type": "market_analyzer_v1_operator_dashboard",
        "event_theme": event_theme,
        "expected_behavior": event_theme.replace("_", " "),
        "symbol": symbol,
        "headline": headline,
        "classification": _classification_block(),
        "case_panel": {
            "case_id": request_id,
            "title": headline,
        },
        "runtime_panel": {
            "headline": headline,
            "event_theme": event_theme,
            "market_regime": _safe_dict(routed.get("market_regime_record")).get(
                "regime", "unknown"
            ),
            "macro_bias": _safe_dict(routed.get("market_regime_record")).get(
                "macro_bias", "neutral"
            ),
        },
        "market_panel": {
            "symbol": symbol,
            "headline": headline,
            "event_theme": event_theme,
            "price": payload.get("price"),
            "reference_price": payload.get("price") or payload.get("reference_price"),
            "price_at_closeout": payload.get("price") or payload.get("reference_price"),
            "price_change_pct": _safe_float(payload.get("price_change_pct"), 0.0),
            "sector": _safe_str(payload.get("sector"), default="unknown"),
            "confirmation": _safe_str(payload.get("confirmation"), default="partial"),
            "source_refs": _safe_list(payload.get("source_refs")),
        },
        "recommendation_panel": {
            "state": "present" if recommendations else "empty",
            "count": len(recommendations),
            "items": recommendations,
        },
        "governance_panel": {
            "approval_required": True,
            "execution_allowed": False,
            "route_path": "pm_route",
            "source_flow": (
                "source/provider signal -> RESEARCH_CORE -> engine curation -> "
                "adapter shaping -> PM interpretation -> route -> child-core ingress"
            ),
        },
        "rejection_panel": {
            "status": routed.get("status"),
            "reason": routed.get("reason", ""),
        }
        if routed.get("status") != "ok"
        else {},
        "authority": {
            **_authority_block(),
            "advisory_only": True,
            "can_mutate_workflow_state": False,
            "can_mutate_provider_truth": False,
            "source_is_engine_curated": bool(payload.get("curated_live_source")),
        },
        "routed_result": routed,
        "lineage": {
            "api_surface": "AI_GO.api.market_analyzer_api",
            "pm_authority": "AI_GO.core.strategy.pm_market_analyzer_route",
            "checked_at": _utc_now_iso(),
        },
    }

    if isinstance(payload.get("curated_live_source"), dict):
        final_payload["curated_live_source"] = payload["curated_live_source"]

    return final_payload


def _attach_lineage(
    *,
    result: Dict[str, Any],
    payload: Dict[str, Any],
    request: Request,
    operator_id: str,
    endpoint: str,
    raw_mode: bool,
) -> Dict[str, Any]:
    request_id = _safe_str(payload.get("request_id")) or _safe_str(result.get("request_id"))
    case_id = _safe_str(payload.get("case_id")) or _safe_str(result.get("request_id")) or request_id
    route_mode = _safe_str(result.get("route_mode"), default="pm_route")

    receipt = build_run_receipt(
        request=request,
        request_id=request_id,
        case_id=case_id,
        api_key_id=operator_id,
        route_mode=route_mode,
        core_id="market_analyzer_v1",
        endpoint=endpoint,
        raw_mode=raw_mode,
    )
    receipt_path = persist_receipt(receipt)

    watcher_result = validate_market_analyzer_receipt(receipt)
    watcher_path = persist_validation_result(watcher_result)

    closeout = create_closeout_artifact(
        receipt_payload=receipt,
        watcher_receipt=watcher_result,
        system_view=result,
    )

    enriched = dict(result)
    enriched["receipt_id"] = receipt["receipt_id"]
    enriched["receipt_path"] = str(receipt_path)
    enriched["watcher_validation_id"] = watcher_result["validation_id"]
    enriched["watcher_status"] = watcher_result["watcher_status"]
    enriched["watcher_path"] = str(watcher_path)
    enriched["closeout_id"] = closeout["closeout_id"]
    enriched["closeout_status"] = closeout["closeout_status"]
    enriched["closeout_path"] = closeout["path"]

    return enriched


def _log_failure(
    *,
    event_type_failure: str,
    request: Request,
    operator_id: str,
    request_id: str,
) -> None:
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


def _execute_market_route(
    *,
    payload: Dict[str, Any],
    request: Request,
    operator_id: str,
    event_type_success: str,
    event_type_failure: str,
    endpoint: str,
    latest_live: bool,
    raw_mode: bool,
) -> Dict[str, Any]:
    request_id = _ensure_request_id(payload)
    payload["request_id"] = request_id
    _basic_validate(payload)

    try:
        pm_packet = _build_pm_packet(payload)
        routed = route_market_analyzer_packet(pm_packet)

        final_payload = _build_operator_payload(
            payload=payload,
            routed=routed,
        )

        final_payload = _attach_lineage(
            result=final_payload,
            payload=payload,
            request=request,
            operator_id=operator_id,
            endpoint=endpoint,
            raw_mode=raw_mode,
        )

        _persist_request_snapshot(
            final_payload=final_payload,
            latest_live=latest_live,
        )

        log_request_event(
            event_type=event_type_success,
            route=str(request.url.path),
            method=request.method,
            status_code=status.HTTP_200_OK,
            operator_id=operator_id,
            client_host=_client_host(request),
            request_id=final_payload.get("request_id") or request_id,
            route_mode=final_payload.get("route_mode"),
            outcome="success",
        )

        return final_payload

    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        _log_failure(
            event_type_failure=event_type_failure,
            request=request,
            operator_id=operator_id,
            request_id=request_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "api_version": MARKET_ANALYZER_API_VERSION,
        "mode": "northstar_governed",
        "execution_allowed": False,
        "mutation_allowed": False,
        "raw_live_route_enabled": False,
        "curated_live_route_enabled": True,
    }


@router.get("/operator/latest")
def latest_operator_payload() -> Dict[str, Any]:
    return read_latest_operator_payload()


@router.post("/run")
async def run_market_analyzer(
    payload: Dict[str, Any],
    request: Request,
    operator_id: str = Depends(require_api_key),
    _: None = Depends(enforce_rate_limit),
) -> Dict[str, Any]:
    return _execute_market_route(
        payload=payload,
        request=request,
        operator_id=operator_id,
        event_type_success="market_analyzer_run",
        event_type_failure="market_analyzer_run_failed",
        endpoint="/market-analyzer/run",
        latest_live=False,
        raw_mode=False,
    )


@router.post("/run/live")
async def run_market_analyzer_live(
    payload: Dict[str, Any],
    request: Request,
    operator_id: str = Depends(require_api_key),
    _: None = Depends(enforce_rate_limit),
) -> Dict[str, Any]:
    try:
        enforce_route_level_access(
            route="/market-analyzer/run/live",
            method=request.method,
            payload=payload,
            actor=operator_id,
        )
    except PermissionError as exc:
        log_request_event(
            event_type="market_analyzer_live_route_blocked",
            route=str(request.url.path),
            method=request.method,
            status_code=status.HTTP_403_FORBIDDEN,
            operator_id=operator_id,
            client_host=_client_host(request),
            request_id=str(payload.get("request_id", "")),
            outcome="blocked_by_route_level_enforcement",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=exc.args[0] if exc.args else "route_level_access_blocked",
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "error": "legacy_raw_live_route_disabled",
            "message": (
                "Direct live Market Analyzer route is disabled. "
                "Use /market-analyzer/run/curated-live with a governed engine_handoff_packet."
            ),
            "execution_allowed": False,
            "approval_required": True,
        },
    )


@router.post("/run/curated-live")
async def run_market_analyzer_curated_live(
    payload: Dict[str, Any],
    request: Request,
    operator_id: str = Depends(require_api_key),
    _: None = Depends(enforce_rate_limit),
) -> Dict[str, Any]:
    try:
        enforce_route_level_access(
            route="/market-analyzer/run/curated-live",
            method=request.method,
            payload=payload,
            actor=operator_id,
        )
    except PermissionError as exc:
        log_request_event(
            event_type="market_analyzer_curated_live_route_blocked",
            route=str(request.url.path),
            method=request.method,
            status_code=status.HTTP_400_BAD_REQUEST,
            operator_id=operator_id,
            client_host=_client_host(request),
            request_id=str(payload.get("request_id", "")),
            outcome="blocked_by_route_level_enforcement",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.args[0] if exc.args else "route_level_access_blocked",
        )

    curated_live_payload = _build_live_input_from_engine_handoff(payload)

    return _execute_market_route(
        payload=curated_live_payload,
        request=request,
        operator_id=operator_id,
        event_type_success="market_analyzer_curated_live_run",
        event_type_failure="market_analyzer_curated_live_run_failed",
        endpoint="/market-analyzer/run/curated-live",
        latest_live=True,
        raw_mode=False,
    )