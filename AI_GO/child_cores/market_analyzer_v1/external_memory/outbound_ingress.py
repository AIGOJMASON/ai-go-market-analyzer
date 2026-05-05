# AI_GO/child_cores/market_analyzer_v1/external_memory/outbound_ingress.py

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Dict, List


class OutboundMemoryIngressError(ValueError):
    pass


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True
        if normalized in {"false", "0", "no", "off"}:
            return False
    return bool(value)


def _as_dict(value: Any) -> Dict[str, Any]:
    return deepcopy(value) if isinstance(value, dict) else {}


def _as_list(value: Any) -> List[Any]:
    return deepcopy(value) if isinstance(value, list) else []


def _require_str(mapping: Dict[str, Any], key: str) -> str:
    value = _safe_str(mapping.get(key))
    if not value:
        raise OutboundMemoryIngressError(f"Missing required field: {key}")
    return value


def _normalize_case_panel(result: Dict[str, Any]) -> Dict[str, Any]:
    case_panel = _as_dict(result.get("case_panel"))
    if case_panel:
        return case_panel

    return {
        "case_id": _safe_str(result.get("request_id"), _safe_str(result.get("case_id"))),
        "title": _safe_str(result.get("headline")),
    }


def _normalize_runtime_panel(result: Dict[str, Any]) -> Dict[str, Any]:
    runtime_panel = _as_dict(result.get("runtime_panel"))
    if runtime_panel:
        return runtime_panel

    market_panel = _as_dict(result.get("market_panel"))
    if market_panel:
        return market_panel

    market_regime_record = _as_dict(result.get("market_regime_record"))
    event_propagation_record = _as_dict(result.get("event_propagation_record"))

    return {
        "market_regime": _safe_str(market_regime_record.get("regime"), "unknown"),
        "event_theme": _safe_str(event_propagation_record.get("theme")),
        "macro_bias": _safe_str(market_regime_record.get("macro_bias"), "unknown"),
        "headline": _safe_str(event_propagation_record.get("headline"), _safe_str(result.get("headline"))),
        "sector": _safe_str(result.get("sector")),
    }


def _normalize_recommendation_panel(result: Dict[str, Any]) -> Dict[str, Any]:
    existing = _as_dict(result.get("recommendation_panel"))
    if existing:
        return existing

    trade_packet = _as_dict(result.get("trade_recommendation_packet"))
    recommendations = _as_list(trade_packet.get("recommendations"))

    items: List[Dict[str, Any]] = []
    for recommendation in recommendations:
        if not isinstance(recommendation, dict):
            continue

        item = {
            "symbol": _safe_str(recommendation.get("symbol")),
            "entry": _safe_str(recommendation.get("entry")),
            "exit": _safe_str(recommendation.get("exit")),
            "confidence": _safe_str(recommendation.get("confidence")),
        }
        if any(item.values()):
            items.append(item)

    if not items:
        return {}

    return {
        "state": "present",
        "count": len(items),
        "items": items,
    }


def _normalize_governance_panel(result: Dict[str, Any]) -> Dict[str, Any]:
    existing = _as_dict(result.get("governance_panel"))
    if existing:
        return existing

    approval_packet = _as_dict(result.get("approval_request_packet"))
    receipt_trace_packet = _as_dict(result.get("receipt_trace_packet"))
    watcher = _as_dict(result.get("watcher"))

    return {
        "approval_required": _safe_bool(result.get("approval_required"), default=True),
        "execution_allowed": _safe_bool(result.get("execution_allowed"), default=False),
        "approval_gate": _safe_str(approval_packet.get("approval_gate")),
        "route_path": _safe_str(receipt_trace_packet.get("path")),
        "watcher_passed": watcher.get("passed"),
    }


def _derive_symbol_and_sector(
    recommendation_panel: Dict[str, Any],
    source_result: Dict[str, Any],
) -> tuple[str, str]:
    sector = _safe_str(source_result.get("sector"))
    if not sector:
        runtime_panel = _as_dict(source_result.get("runtime_panel"))
        sector = _safe_str(runtime_panel.get("sector"))
    if not sector:
        market_panel = _as_dict(source_result.get("market_panel"))
        sector = _safe_str(market_panel.get("sector"))

    items = recommendation_panel.get("items")
    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict):
                symbol = _safe_str(item.get("symbol"))
                if symbol:
                    return symbol, sector

    return (
        _safe_str(source_result.get("symbol")),
        sector,
    )


def _derive_confidence_posture(
    recommendation_panel: Dict[str, Any],
    source_result: Dict[str, Any],
) -> str:
    items = recommendation_panel.get("items")
    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict):
                confidence = _safe_str(item.get("confidence"))
                if confidence:
                    return confidence

    refinement_panel = _as_dict(source_result.get("refinement_panel"))
    confidence_adjustment = _safe_str(refinement_panel.get("confidence_adjustment"))
    if confidence_adjustment:
        return confidence_adjustment

    if _safe_str(source_result.get("status"), "ok") != "ok":
        return "rejected"

    return "unknown"


def _derive_bounded_summary(
    case_panel: Dict[str, Any],
    runtime_panel: Dict[str, Any],
    recommendation_panel: Dict[str, Any],
    governance_panel: Dict[str, Any],
    source_result: Dict[str, Any],
) -> str:
    headline = _safe_str(runtime_panel.get("headline"), _safe_str(case_panel.get("title"), "Untitled event"))
    event_theme = _safe_str(runtime_panel.get("event_theme"), "unknown_theme")
    market_regime = _safe_str(runtime_panel.get("market_regime"), "unknown_regime")
    macro_bias = _safe_str(runtime_panel.get("macro_bias"), "unknown_bias")
    status = _safe_str(source_result.get("status"), "unknown_status")
    approval_required = _safe_bool(governance_panel.get("approval_required"), default=True)

    item_summary = "no recommendation"
    items = recommendation_panel.get("items")
    if isinstance(items, list) and items:
        first_item = items[0] if isinstance(items[0], dict) else {}
        symbol = _safe_str(first_item.get("symbol"), "unknown_symbol")
        entry = _safe_str(first_item.get("entry"), "unspecified_entry")
        confidence = _safe_str(first_item.get("confidence"), "unknown_confidence")
        item_summary = f"{symbol} at {entry} with {confidence} confidence"

    return (
        f"{headline}; theme={event_theme}; regime={market_regime}; "
        f"macro_bias={macro_bias}; routed_status={status}; "
        f"recommendation={item_summary}; approval_required={str(approval_required).lower()}"
    )


def _build_source_lineage(
    source_result: Dict[str, Any],
    target_child_core_id: str,
) -> Dict[str, Any]:
    lineage: Dict[str, Any] = {
        "target_child_core_id": target_child_core_id,
        "route_mode": _safe_str(source_result.get("route_mode"), "pm_route"),
        "mode": _safe_str(source_result.get("mode"), "advisory"),
        "status": _safe_str(source_result.get("status"), "unknown"),
        "watcher_status": _safe_str(source_result.get("watcher_status")),
        "closeout_status": _safe_str(source_result.get("closeout_status")),
    }

    optional_fields = [
        "receipt_id",
        "receipt_path",
        "watcher_validation_id",
        "watcher_path",
        "closeout_id",
        "closeout_path",
    ]
    for key in optional_fields:
        value = _safe_str(source_result.get(key))
        if value:
            lineage[key] = value

    return lineage


def _build_record_id(
    *,
    request_id: str,
    symbol: str,
    event_theme: str,
    closeout_id: str,
) -> str:
    seed = "|".join(
        [
            request_id,
            symbol,
            event_theme,
            closeout_id,
        ]
    )
    digest = sha256(seed.encode("utf-8")).hexdigest()[:12]
    return f"external_memory_ingress_{request_id}_{digest}"


def build_outbound_memory_ingress_record(
    child_core_result: Dict[str, Any],
    *,
    target_child_core_id: str = "market_analyzer_v1",
    source_type: str = "child_core_output",
) -> Dict[str, Any]:
    if not isinstance(child_core_result, dict):
        raise OutboundMemoryIngressError("child_core_result must be a dict")

    source_result = deepcopy(child_core_result)

    request_id = _require_str(source_result, "request_id")
    closeout_status = _require_str(source_result, "closeout_status")
    if closeout_status != "accepted":
        raise OutboundMemoryIngressError(
            "Outbound memory ingress requires closeout_status='accepted'"
        )

    case_panel = _normalize_case_panel(source_result)
    runtime_panel = _normalize_runtime_panel(source_result)
    recommendation_panel = _normalize_recommendation_panel(source_result)
    governance_panel = _normalize_governance_panel(source_result)

    event_theme = _safe_str(runtime_panel.get("event_theme"))
    if not event_theme:
        raise OutboundMemoryIngressError("Unable to derive event_theme from child_core_result")

    symbol, sector = _derive_symbol_and_sector(recommendation_panel, source_result)
    confidence_posture = _derive_confidence_posture(recommendation_panel, source_result)
    bounded_summary = _derive_bounded_summary(
        case_panel=case_panel,
        runtime_panel=runtime_panel,
        recommendation_panel=recommendation_panel,
        governance_panel=governance_panel,
        source_result=source_result,
    )

    source_lineage = _build_source_lineage(source_result, target_child_core_id)
    closeout_id = _require_str(source_lineage, "closeout_id")

    ingress_record = {
        "record_type": "external_memory_ingress_record",
        "record_version": "v1",
        "record_id": _build_record_id(
            request_id=request_id,
            symbol=symbol or "unknown_symbol",
            event_theme=event_theme,
            closeout_id=closeout_id,
        ),
        "created_at": _utc_now_iso(),
        "source_type": source_type,
        "target_child_core_id": target_child_core_id,
        "request_id": request_id,
        "symbol": symbol,
        "sector": sector,
        "event_theme": event_theme,
        "confidence_posture": confidence_posture,
        "bounded_summary": bounded_summary,
        "source_lineage": source_lineage,
        "admission_contract": {
            "qualification_required": True,
            "persistence_gate_required": True,
            "db_writer_required": True,
            "retrieval_allowed_here": False,
            "promotion_allowed_here": False,
            "return_path_allowed_here": False,
            "output_merge_allowed_here": False,
        },
        "governance_posture": {
            "mode": "advisory",
            "execution_allowed": False,
            "approval_required": _safe_bool(governance_panel.get("approval_required"), default=True),
            "watcher_status": _safe_str(source_lineage.get("watcher_status")),
            "closeout_status": closeout_status,
        },
        "bounded_context": {
            "headline": _safe_str(runtime_panel.get("headline"), _safe_str(case_panel.get("title"))),
            "market_regime": _safe_str(runtime_panel.get("market_regime")),
            "macro_bias": _safe_str(runtime_panel.get("macro_bias")),
            "sector": sector,
            "recommendation_count": recommendation_panel.get("count", 0),
        },
    }

    return ingress_record