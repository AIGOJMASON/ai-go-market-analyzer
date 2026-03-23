from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from .event_propagation_classifier import classify_event_propagation
from .ingress_processor import IngressValidationError, process_ingress
from .market_regime_classifier import classify_market_regime
from .necessity_filter import filter_necessity_candidates
from .rebound_validator import validate_rebounds
from .recommendation_builder import build_recommendations
from .refinement_conditioning import apply_refinement_conditioning


class MarketAnalyzerRuntimeError(Exception):
    """Raised when runtime cannot lawfully produce an output."""


def _build_receipt_trace(
    ingress: Dict[str, Any],
    regime_record: Dict[str, Any],
    propagation_record: Dict[str, Any],
    filtered_record: Dict[str, Any],
    rebound_record: Dict[str, Any],
    recommendation_packet: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact_type": "receipt_trace_packet",
        "core_id": "market_analyzer_v1",
        "upstream_receipt": deepcopy(ingress.get("receipt")),
        "trace": {
            "regime_artifact": regime_record.get("artifact_type"),
            "propagation_artifact": propagation_record.get("artifact_type"),
            "filter_artifact": filtered_record.get("artifact_type"),
            "rebound_artifact": rebound_record.get("artifact_type"),
            "recommendation_artifact": recommendation_packet.get("artifact_type"),
        },
    }


def _build_approval_request(
    recommendation_packet: Dict[str, Any],
    trace_packet: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact_type": "approval_request_packet",
        "core_id": "market_analyzer_v1",
        "approval_type": "human_trade_approval_record",
        "recommendation_count": recommendation_packet.get("recommendation_count", 0),
        "execution_allowed": False,
        "trace_reference": trace_packet.get("artifact_type"),
    }


def run(packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Minimal lawful execution path for market_analyzer_v1.

    INGEST -> CONDITION -> REGIME -> PROPAGATION -> FILTER -> VALIDATE -> RECOMMEND -> APPROVAL
    """
    try:
        ingress = process_ingress(packet)
    except IngressValidationError as exc:
        raise MarketAnalyzerRuntimeError(str(exc)) from exc

    conditioning = apply_refinement_conditioning(ingress)
    regime_record = classify_market_regime(ingress.get("market_context", {}))
    propagation_record = classify_event_propagation(ingress.get("event", {}))

    if not propagation_record.get("shock_confirmed", False):
        raise MarketAnalyzerRuntimeError("shock event is required for recommendation flow")

    filtered_record = filter_necessity_candidates(ingress.get("candidates", []))
    if filtered_record.get("filtered_count", 0) == 0:
        raise MarketAnalyzerRuntimeError("no necessity-qualified candidates available")

    rebound_record = validate_rebounds(filtered_record["filtered_candidates"])
    if rebound_record.get("validated_count", 0) == 0:
        raise MarketAnalyzerRuntimeError("no rebound-validated candidates available")

    recommendation_packet = build_recommendations(
        rebound_record["validated_candidates"],
        regime_record,
        propagation_record,
        conditioning,
    )

    trace_packet = _build_receipt_trace(
        ingress=ingress,
        regime_record=regime_record,
        propagation_record=propagation_record,
        filtered_record=filtered_record,
        rebound_record=rebound_record,
        recommendation_packet=recommendation_packet,
    )

    approval_request_packet = _build_approval_request(
        recommendation_packet=recommendation_packet,
        trace_packet=trace_packet,
    )

    return {
        "core_id": "market_analyzer_v1",
        "status": "ok",
        "artifacts": {
            "market_regime_record": regime_record,
            "event_propagation_record": propagation_record,
            "necessity_filtered_candidate_set": filtered_record,
            "rebound_validation_record": rebound_record,
            "trade_recommendation_packet": recommendation_packet,
            "receipt_trace_packet": trace_packet,
            "approval_request_packet": approval_request_packet,
        },
    }