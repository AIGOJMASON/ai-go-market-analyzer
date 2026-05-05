# AI_GO/child_cores/market_analyzer_v1/ui/live_data_runner.py

from __future__ import annotations

import importlib
import json
from typing import Any, Callable, Dict, Optional

from .live_data_adapter import normalize_live_input
from .live_data_source import get_default_live_style_case, get_live_style_case

try:
    from AI_GO.child_cores.ingress.canonical_live_ingress import (
        build_canonical_live_pm_packet,
    )
except ModuleNotFoundError:
    from child_cores.ingress.canonical_live_ingress import (  # type: ignore
        build_canonical_live_pm_packet,
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


def _extract_recommendation_panel(routed_result: Dict[str, Any]) -> Dict[str, Any]:
    recommendation_packet = routed_result.get("trade_recommendation_packet", {})
    recommendations = recommendation_packet.get("recommendations", [])

    if not isinstance(recommendation_packet, dict):
        recommendation_packet = {}

    if not isinstance(recommendations, list):
        recommendations = []

    return {
        "recommendation_count": recommendation_packet.get(
            "recommendation_count",
            len(recommendations),
        ),
        "recommendations": recommendations,
    }


def _extract_governance_panel(routed_result: Dict[str, Any]) -> Dict[str, Any]:
    receipt_trace_packet = routed_result.get("receipt_trace_packet", {})
    watcher = routed_result.get("watcher", {})

    if not isinstance(receipt_trace_packet, dict):
        receipt_trace_packet = {}
    if not isinstance(watcher, dict):
        watcher = {}

    return {
        "watcher_passed": watcher.get("passed"),
        "approval_required": routed_result.get("approval_required"),
        "execution_allowed": routed_result.get("execution_allowed"),
        "receipt_id": receipt_trace_packet.get("receipt_id"),
    }


def _extract_cognition_panel(
    pm_packet: Dict[str, Any],
    routed_result: Dict[str, Any],
) -> Dict[str, Any]:
    event_context = pm_packet.get("event_context", {})
    if not isinstance(event_context, dict):
        event_context = {}

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
            "next_step_class": approval_packet.get(
                "approval_gate",
                "human_trade_approval_record",
            ),
        }
    }


def _build_live_response(
    pm_packet: Dict[str, Any],
    raw_payload: Dict[str, Any],
    routed_result: Dict[str, Any],
) -> Dict[str, Any]:
    event_context = pm_packet.get("event_context", {})
    if not isinstance(event_context, dict):
        event_context = {}

    market_regime_record = routed_result.get("market_regime_record", {})
    event_propagation_record = routed_result.get("event_propagation_record", {})

    if not isinstance(market_regime_record, dict):
        market_regime_record = {}
    if not isinstance(event_propagation_record, dict):
        event_propagation_record = {}

    recommendation_panel = _extract_recommendation_panel(routed_result)
    governance_panel = _extract_governance_panel(routed_result)
    cognition_panel = _extract_cognition_panel(pm_packet, routed_result)
    pm_workflow_panel = _extract_pm_workflow_panel(routed_result)

    rejection_panel = None
    if routed_result.get("status") != "ok":
        rejection_panel = {
            "reason": routed_result.get("reason", "live_route_rejected"),
        }

    return {
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
            "event_theme": event_propagation_record.get(
                "theme",
                event_context.get("theme"),
            ),
            "macro_bias": market_regime_record.get(
                "macro_bias",
                event_context.get("macro_bias", "mixed"),
            ),
            "headline": _safe_str(
                raw_payload.get("headline"),
                event_context.get("headline"),
            ),
        },
        "runtime_panel": {
            "market_regime": market_regime_record.get("regime", "normal"),
            "event_theme": event_propagation_record.get(
                "theme",
                event_context.get("theme"),
            ),
            "macro_bias": market_regime_record.get(
                "macro_bias",
                event_context.get("macro_bias", "mixed"),
            ),
            "headline": _safe_str(
                raw_payload.get("headline"),
                event_context.get("headline"),
            ),
        },
        "recommendation_panel": recommendation_panel,
        "cognition_panel": cognition_panel,
        "refinement_panel": cognition_panel,
        "pm_workflow_panel": pm_workflow_panel,
        "governance_panel": governance_panel,
        "rejection_panel": rejection_panel,
    }


def run_live_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise LiveDataRunnerError("payload must be a dict")

    normalized_packet = normalize_live_input(payload)
    if hasattr(normalized_packet, "model_dump"):
        normalized_packet = normalized_packet.model_dump(
            by_alias=True,
            exclude_none=False,
        )

    if not isinstance(normalized_packet, dict):
        raise LiveDataRunnerError(
            "normalize_live_input returned unsupported result type"
        )

    request_id = _safe_str(
        normalized_packet.get("case_id"),
        _safe_str(payload.get("request_id"), "live-request"),
    )
    pm_packet = build_canonical_live_pm_packet(payload, request_id)

    pm_route = _resolve_pm_route_callable()
    routed_result = pm_route(pm_packet)

    if hasattr(routed_result, "model_dump"):
        routed_result = routed_result.model_dump(by_alias=True, exclude_none=False)

    if not isinstance(routed_result, dict):
        raise LiveDataRunnerError("PM route returned unsupported result type")

    return _build_live_response(
        pm_packet=pm_packet,
        raw_payload=payload,
        routed_result=routed_result,
    )


def run_live_case(case_id: Optional[str] = None) -> Dict[str, Any]:
    raw_case = get_default_live_style_case() if case_id is None else get_live_style_case(case_id)
    return run_live_payload(raw_case)


if __name__ == "__main__":
    result = run_live_case()
    print(json.dumps(result, indent=2))