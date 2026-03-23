from __future__ import annotations

from typing import Any, Dict, List


class PMMarketAnalyzerRouteError(ValueError):
    pass


def _require(mapping: Dict[str, Any], key: str) -> Any:
    if key not in mapping:
        raise PMMarketAnalyzerRouteError(f"Missing required field: {key}")
    return mapping[key]


def _validate_packet(packet: Dict[str, Any]) -> None:
    if not isinstance(packet, dict):
        raise PMMarketAnalyzerRouteError("Packet must be a dictionary.")

    packet_type = _require(packet, "packet_type")
    parent_authority = _require(packet, "parent_authority")
    target_core = _require(packet, "target_core")
    candidates = _require(packet, "candidates")
    event_context = _require(packet, "event_context")

    if packet_type != "pm_style_live_input":
        raise PMMarketAnalyzerRouteError(
            f"Unsupported packet_type: {packet_type}"
        )

    if parent_authority != "PM_CORE":
        raise PMMarketAnalyzerRouteError(
            f"Invalid parent authority: {parent_authority}"
        )

    if target_core != "market_analyzer_v1":
        raise PMMarketAnalyzerRouteError(
            f"Invalid target core: {target_core}"
        )

    if not isinstance(candidates, list) or not candidates:
        raise PMMarketAnalyzerRouteError(
            "At least one candidate is required."
        )

    if not isinstance(event_context, dict):
        raise PMMarketAnalyzerRouteError(
            "event_context must be a dictionary."
        )


def _classify_market_regime(packet: Dict[str, Any]) -> Dict[str, Any]:
    macro_bias = packet["event_context"].get("macro_bias", "neutral")

    if macro_bias in {"supportive", "neutral", "mixed"}:
        regime = "normal"
    else:
        regime = "unsafe"

    return {
        "regime": regime,
        "macro_bias": macro_bias,
    }


def _classify_event_propagation(packet: Dict[str, Any]) -> Dict[str, Any]:
    event_context = packet["event_context"]
    return {
        "theme": event_context.get("theme", "unknown"),
        "propagation": event_context.get("propagation", "unknown"),
        "confirmed": bool(event_context.get("confirmed", False)),
        "headline": event_context.get("headline", ""),
    }


def _filter_necessity_candidates(packet: Dict[str, Any]) -> List[Dict[str, Any]]:
    filtered: List[Dict[str, Any]] = []

    for candidate in packet["candidates"]:
        if candidate.get("necessity_qualified") is True:
            filtered.append(candidate)

    return filtered


def _validate_rebound_candidates(
    candidates: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    validated: List[Dict[str, Any]] = []

    for candidate in candidates:
        if candidate.get("rebound_confirmed") is True:
            validated.append(candidate)

    return validated


def _build_trade_recommendation_packet(
    candidates: List[Dict[str, Any]],
) -> Dict[str, Any]:
    recommendations: List[Dict[str, Any]] = []

    for candidate in candidates:
        recommendations.append(
            {
                "symbol": candidate["symbol"],
                "entry": candidate.get("entry_signal", "unspecified"),
                "exit": candidate.get("exit_signal", "unspecified"),
                "confidence": candidate.get("confidence", "unknown"),
            }
        )

    return {
        "recommendation_count": len(recommendations),
        "recommendations": recommendations,
    }


def _build_receipt_trace_packet(
    packet: Dict[str, Any],
    outcome: str,
) -> Dict[str, Any]:
    return {
        "receipt_id": f"{packet['case_id']}-{outcome}-PM-001",
        "path": "PM_CORE->market_analyzer_v1",
        "target_core": "market_analyzer_v1",
        "parent_authority": "PM_CORE",
        "execution_allowed": False,
    }


def _build_approval_request_packet() -> Dict[str, Any]:
    return {
        "approval_gate": "human_trade_approval_record",
        "approval_required": True,
        "execution_allowed": False,
    }


def route_market_analyzer_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    _validate_packet(packet)

    market_regime_record = _classify_market_regime(packet)
    event_propagation_record = _classify_event_propagation(packet)

    if market_regime_record["regime"] == "unsafe":
        return {
            "status": "rejected",
            "reason": "unsafe_market_regime",
            "market_regime_record": market_regime_record,
            "event_propagation_record": event_propagation_record,
            "necessity_filtered_candidate_set": [],
            "trade_recommendation_packet": {
                "recommendation_count": 0,
                "recommendations": [],
            },
            "approval_request_packet": _build_approval_request_packet(),
            "watcher": {"passed": False},
            "approval_required": True,
            "execution_allowed": False,
            "receipt_trace_packet": _build_receipt_trace_packet(
                packet,
                "REJECT-UNSAFE",
            ),
        }

    if not event_propagation_record["confirmed"]:
        return {
            "status": "rejected",
            "reason": "event_not_confirmed",
            "market_regime_record": market_regime_record,
            "event_propagation_record": event_propagation_record,
            "necessity_filtered_candidate_set": [],
            "trade_recommendation_packet": {
                "recommendation_count": 0,
                "recommendations": [],
            },
            "approval_request_packet": _build_approval_request_packet(),
            "watcher": {"passed": False},
            "approval_required": True,
            "execution_allowed": False,
            "receipt_trace_packet": _build_receipt_trace_packet(
                packet,
                "REJECT-UNCONFIRMED",
            ),
        }

    necessity_filtered_candidate_set = _filter_necessity_candidates(packet)
    rebound_validated_candidates = _validate_rebound_candidates(
        necessity_filtered_candidate_set
    )

    if not rebound_validated_candidates:
        return {
            "status": "rejected",
            "reason": "no rebound-validated candidates available",
            "market_regime_record": market_regime_record,
            "event_propagation_record": event_propagation_record,
            "necessity_filtered_candidate_set": necessity_filtered_candidate_set,
            "trade_recommendation_packet": {
                "recommendation_count": 0,
                "recommendations": [],
            },
            "approval_request_packet": _build_approval_request_packet(),
            "watcher": {"passed": False},
            "approval_required": True,
            "execution_allowed": False,
            "receipt_trace_packet": _build_receipt_trace_packet(
                packet,
                "REJECT-NOREBOUND",
            ),
        }

    trade_recommendation_packet = _build_trade_recommendation_packet(
        rebound_validated_candidates
    )

    return {
        "status": "ok",
        "market_regime_record": market_regime_record,
        "event_propagation_record": event_propagation_record,
        "necessity_filtered_candidate_set": rebound_validated_candidates,
        "trade_recommendation_packet": trade_recommendation_packet,
        "approval_request_packet": _build_approval_request_packet(),
        "watcher": {"passed": True},
        "approval_required": True,
        "execution_allowed": False,
        "receipt_trace_packet": _build_receipt_trace_packet(
            packet,
            "OK",
        ),
    }


def route_market_analyzer_request(packet: Dict[str, Any]) -> Dict[str, Any]:
    return route_market_analyzer_packet(packet)


def route_request(packet: Dict[str, Any]) -> Dict[str, Any]:
    return route_market_analyzer_packet(packet)


def run_route(packet: Dict[str, Any]) -> Dict[str, Any]:
    return route_market_analyzer_packet(packet)


def run(packet: Dict[str, Any]) -> Dict[str, Any]:
    return route_market_analyzer_packet(packet)