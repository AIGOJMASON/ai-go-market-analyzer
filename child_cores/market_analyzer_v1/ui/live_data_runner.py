from __future__ import annotations

import importlib
import json
from typing import Any, Callable, Dict, List, Optional

from .live_data_adapter import normalize_live_input
from .live_data_source import get_default_live_style_case, get_live_style_case

try:
    from AI_GO.child_cores.market_analyzer_v1.external_memory.runtime_path import (
        run_market_analyzer_external_memory_path,
    )
except ModuleNotFoundError:
    from child_cores.market_analyzer_v1.external_memory.runtime_path import (
        run_market_analyzer_external_memory_path,
    )


class LiveDataRunnerError(RuntimeError):
    pass


def _resolve_pm_route_callable() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    module_names = (
        "AI_GO.core.strategy.pm_market_analyzer_route",
        "core.strategy.pm_market_analyzer_route",
    )
    candidate_function_names = (
        "route_market_analyzer_request",
        "route_market_analyzer_packet",
        "route_request",
        "run_route",
        "run",
    )

    last_error: Exception | None = None

    for module_name in module_names:
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            continue

        for function_name in candidate_function_names:
            candidate = getattr(module, function_name, None)
            if callable(candidate):
                return candidate

    if last_error is not None:
        raise LiveDataRunnerError(
            "PM market analyzer route module could not be resolved."
        ) from last_error

    raise LiveDataRunnerError(
        "PM market analyzer route callable could not be found."
    )


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _truthy_confirmation(value: Any) -> bool:
    normalized = _safe_str(value).lower()
    return normalized in {"confirmed", "partial", "true", "yes", "1"}


def _normalize_macro_bias(normalized_packet: Dict[str, Any], raw_payload: Dict[str, Any]) -> str:
    event_context = normalized_packet.get("event_context", {})
    candidate = _safe_str(event_context.get("macro_bias"))
    if candidate:
        return candidate

    sector = _safe_str(raw_payload.get("sector")).lower()
    if sector in {"energy", "utilities", "consumer_staples", "healthcare"}:
        return "supportive"
    if sector in {"technology", "consumer_discretionary", "communication_services"}:
        return "mixed"
    return "neutral"


def _normalize_theme(normalized_packet: Dict[str, Any], raw_payload: Dict[str, Any]) -> str:
    event_context = normalized_packet.get("event_context", {})
    candidate = _safe_str(event_context.get("theme"))
    if candidate:
        return candidate

    sector = _safe_str(raw_payload.get("sector")).lower()
    confirmation = _safe_str(raw_payload.get("confirmation")).lower()

    if sector == "energy":
        return "energy_rebound" if confirmation in {"confirmed", "partial"} else "energy_move"
    if sector in {"utilities", "consumer_staples", "healthcare"}:
        return "necessity_rebound"
    return "speculative_move"


def _normalize_propagation(normalized_packet: Dict[str, Any], raw_payload: Dict[str, Any]) -> str:
    event_context = normalized_packet.get("event_context", {})
    candidate = _safe_str(event_context.get("propagation"))
    if candidate:
        return candidate

    price_change_pct = _safe_float(raw_payload.get("price_change_pct"), 0.0)
    if abs(price_change_pct) >= 3.0:
        return "fast"
    if abs(price_change_pct) >= 1.0:
        return "moderate"
    return "limited"


def _build_candidate_from_payload(raw_payload: Dict[str, Any]) -> Dict[str, Any]:
    symbol = _safe_str(raw_payload.get("symbol"), "UNKNOWN")
    sector = _safe_str(raw_payload.get("sector")).lower()
    confirmation = _safe_str(raw_payload.get("confirmation")).lower()
    price_change_pct = _safe_float(raw_payload.get("price_change_pct"), 0.0)

    necessity_qualified = sector in {"energy", "utilities", "consumer_staples", "healthcare", "materials"}
    rebound_confirmed = confirmation in {"confirmed", "partial"}

    if price_change_pct >= 3.0:
        confidence = "high"
    elif price_change_pct >= 1.5:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "symbol": symbol,
        "necessity_qualified": necessity_qualified,
        "rebound_confirmed": rebound_confirmed,
        "entry_signal": "reclaim support",
        "exit_signal": "short-term resistance",
        "confidence": confidence,
    }


def _normalize_candidates(normalized_packet: Dict[str, Any], raw_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    candidates = normalized_packet.get("candidates")
    if isinstance(candidates, list) and candidates:
        normalized_list: List[Dict[str, Any]] = []
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue

            normalized_list.append(
                {
                    "symbol": _safe_str(candidate.get("symbol"), _safe_str(raw_payload.get("symbol"), "UNKNOWN")),
                    "necessity_qualified": bool(candidate.get("necessity_qualified", False)),
                    "rebound_confirmed": bool(candidate.get("rebound_confirmed", False)),
                    "entry_signal": _safe_str(candidate.get("entry_signal"), "reclaim support"),
                    "exit_signal": _safe_str(candidate.get("exit_signal"), "short-term resistance"),
                    "confidence": _safe_str(candidate.get("confidence"), "unknown"),
                }
            )

        if normalized_list:
            return normalized_list

    return [_build_candidate_from_payload(raw_payload)]


def _build_pm_packet(normalized_packet: Dict[str, Any], raw_payload: Dict[str, Any]) -> Dict[str, Any]:
    request_id = _safe_str(raw_payload.get("request_id"), "live-request")
    headline = _safe_str(raw_payload.get("headline"), "Live market event")
    confirmed = _truthy_confirmation(raw_payload.get("confirmation"))

    event_context = normalized_packet.get("event_context")
    if not isinstance(event_context, dict):
        event_context = {}

    pm_packet = {
        "packet_type": "pm_style_live_input",
        "parent_authority": "PM_CORE",
        "target_core": "market_analyzer_v1",
        "case_id": _safe_str(normalized_packet.get("case_id"), request_id),
        "headline": _safe_str(normalized_packet.get("headline"), headline),
        "event_context": {
            "theme": _normalize_theme(normalized_packet, raw_payload),
            "propagation": _normalize_propagation(normalized_packet, raw_payload),
            "confirmed": bool(event_context.get("confirmed", confirmed)),
            "headline": _safe_str(event_context.get("headline"), headline),
            "macro_bias": _normalize_macro_bias(normalized_packet, raw_payload),
        },
        "candidates": _normalize_candidates(normalized_packet, raw_payload),
    }

    return pm_packet


def _extract_recommendation_panel(routed_result: Dict[str, Any]) -> Dict[str, Any]:
    recommendation_packet = routed_result.get("trade_recommendation_packet", {})
    recommendations = recommendation_packet.get("recommendations", [])

    if not isinstance(recommendation_packet, dict):
        recommendation_packet = {}

    if not isinstance(recommendations, list):
        recommendations = []

    return {
        "recommendation_count": recommendation_packet.get("recommendation_count", len(recommendations)),
        "recommendations": recommendations,
    }


def _extract_governance_panel(routed_result: Dict[str, Any]) -> Dict[str, Any]:
    receipt_trace_packet = routed_result.get("receipt_trace_packet", {})
    watcher = routed_result.get("watcher", {})

    return {
        "watcher_passed": watcher.get("passed"),
        "approval_required": routed_result.get("approval_required"),
        "execution_allowed": routed_result.get("execution_allowed"),
        "receipt_id": receipt_trace_packet.get("receipt_id"),
    }


def _extract_cognition_panel(pm_packet: Dict[str, Any], routed_result: Dict[str, Any]) -> Dict[str, Any]:
    event_context = pm_packet.get("event_context", {})
    rejection_reason = routed_result.get("reason")

    if rejection_reason == "unsafe_market_regime":
        insight = "Market regime is unsafe for advisory recommendation."
        risk_flag = "unsafe_market_regime"
        confidence_adjustment = "down"
    elif rejection_reason == "event_not_confirmed":
        insight = "Event is not sufficiently confirmed for recommendation."
        risk_flag = "missing_confirmation"
        confidence_adjustment = "down"
    elif rejection_reason == "no rebound-validated candidates available":
        insight = "No rebound-validated candidates are available."
        risk_flag = "no_rebound_candidate"
        confidence_adjustment = "down"
    else:
        insight = "Confirmed necessity rebound candidates support advisory recommendation."
        risk_flag = None
        confidence_adjustment = "none"

    return {
        "signal": event_context.get("theme"),
        "confidence_adjustment": confidence_adjustment,
        "risk_flag": risk_flag,
        "insight": insight,
        "narrative": "Governed output remains advisory and non-executing.",
    }


def _extract_pm_workflow_panel(routed_result: Dict[str, Any]) -> Dict[str, Any]:
    approval_packet = routed_result.get("approval_request_packet", {})
    if not isinstance(approval_packet, dict):
        approval_packet = {}

    if routed_result.get("status") != "ok":
        return {}

    return {
        "planning": {
            "plan_class": "await_human_review",
            "next_step_class": approval_packet.get("approval_gate", "human_trade_approval_record"),
        }
    }


def _run_external_memory(
    raw_payload: Dict[str, Any],
    pm_packet: Dict[str, Any],
    route_mode: str,
) -> Dict[str, Any] | None:
    try:
        return run_market_analyzer_external_memory_path(
            request_id=_safe_str(raw_payload.get("request_id"), pm_packet.get("case_id")),
            symbol=_safe_str(raw_payload.get("symbol"), "UNKNOWN"),
            headline=_safe_str(raw_payload.get("headline"), pm_packet.get("headline")),
            price_change_pct=_safe_float(raw_payload.get("price_change_pct"), 0.0),
            sector=_safe_str(raw_payload.get("sector"), "unknown"),
            confirmation=_safe_str(raw_payload.get("confirmation"), "partial"),
            event_theme=_safe_str(pm_packet.get("event_context", {}).get("theme")),
            macro_bias=_safe_str(pm_packet.get("event_context", {}).get("macro_bias")),
            route_mode=route_mode,
            source_type="live_market_input",
        )
    except Exception:
        return None


def _build_live_response(
    pm_packet: Dict[str, Any],
    raw_payload: Dict[str, Any],
    routed_result: Dict[str, Any],
    external_memory_result: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    event_context = pm_packet.get("event_context", {})
    market_regime_record = routed_result.get("market_regime_record", {})
    event_propagation_record = routed_result.get("event_propagation_record", {})
    recommendation_panel = _extract_recommendation_panel(routed_result)
    governance_panel = _extract_governance_panel(routed_result)
    cognition_panel = _extract_cognition_panel(pm_packet, routed_result)
    pm_workflow_panel = _extract_pm_workflow_panel(routed_result)

    rejection_panel = None
    if routed_result.get("status") != "ok":
        rejection_panel = {
            "reason": routed_result.get("reason", "live_route_rejected"),
        }

    response = {
        "status": "ok" if routed_result.get("status") == "ok" else "rejected",
        "request_id": _safe_str(raw_payload.get("request_id"), pm_packet.get("case_id")),
        "core_id": "market_analyzer_v1",
        "route_mode": "pm_route",
        "mode": "advisory",
        "execution_allowed": bool(routed_result.get("execution_allowed", False)),
        "approval_required": bool(routed_result.get("approval_required", True)),
        "case_panel": {
            "case_id": pm_packet.get("case_id"),
            "title": _safe_str(raw_payload.get("headline"), pm_packet.get("headline")),
            "observed_at": None,
        },
        "market_panel": {
            "market_regime": market_regime_record.get("regime", "normal"),
            "event_theme": event_propagation_record.get("theme", event_context.get("theme")),
            "macro_bias": market_regime_record.get("macro_bias", event_context.get("macro_bias", "mixed")),
            "headline": _safe_str(raw_payload.get("headline"), event_context.get("headline")),
        },
        "runtime_panel": {
            "market_regime": market_regime_record.get("regime", "normal"),
            "event_theme": event_propagation_record.get("theme", event_context.get("theme")),
            "macro_bias": market_regime_record.get("macro_bias", event_context.get("macro_bias", "mixed")),
            "headline": _safe_str(raw_payload.get("headline"), event_context.get("headline")),
        },
        "recommendation_panel": recommendation_panel,
        "cognition_panel": cognition_panel,
        "refinement_panel": cognition_panel,
        "pm_workflow_panel": pm_workflow_panel,
        "governance_panel": governance_panel,
        "rejection_panel": rejection_panel,
    }

    if isinstance(external_memory_result, dict):
        response["external_memory_runtime_result"] = external_memory_result
        response["external_memory_panel"] = external_memory_result.get("panel")
        response["external_memory_retrieval_artifact"] = external_memory_result.get(
            "external_memory_retrieval_artifact"
        )
        response["external_memory_retrieval_receipt"] = external_memory_result.get(
            "external_memory_retrieval_receipt"
        )
        response["external_memory_promotion_artifact"] = external_memory_result.get(
            "external_memory_promotion_artifact"
        )
        response["external_memory_promotion_receipt"] = external_memory_result.get(
            "external_memory_promotion_receipt"
        )

    return response


def run_live_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise LiveDataRunnerError("payload must be a dict")

    normalized_packet = normalize_live_input(payload)
    if hasattr(normalized_packet, "model_dump"):
        normalized_packet = normalized_packet.model_dump(by_alias=True, exclude_none=False)

    if not isinstance(normalized_packet, dict):
        raise LiveDataRunnerError("normalize_live_input returned unsupported result type")

    pm_packet = _build_pm_packet(normalized_packet, payload)
    pm_route = _resolve_pm_route_callable()
    routed_result = pm_route(pm_packet)

    if hasattr(routed_result, "model_dump"):
        routed_result = routed_result.model_dump(by_alias=True, exclude_none=False)

    if not isinstance(routed_result, dict):
        raise LiveDataRunnerError("PM route returned unsupported result type")

    external_memory_result = _run_external_memory(
        raw_payload=payload,
        pm_packet=pm_packet,
        route_mode="pm_route",
    )

    return _build_live_response(
        pm_packet=pm_packet,
        raw_payload=payload,
        routed_result=routed_result,
        external_memory_result=external_memory_result,
    )


def run_live_case(case_id: Optional[str] = None) -> Dict[str, Any]:
    raw_case = get_default_live_style_case() if case_id is None else get_live_style_case(case_id)
    return run_live_payload(raw_case)


if __name__ == "__main__":
    result = run_live_case()
    print(json.dumps(result, indent=2))
