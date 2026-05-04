from __future__ import annotations

from copy import deepcopy
from uuid import uuid4

from AI_GO.core.runtime.refinement.child_core_delivery_registry import (
    APPROVED_ADAPTER_STATUS_VALUES,
    APPROVED_CHILD_CORE_TARGETS,
    APPROVED_DELIVERY_STATUS_VALUES,
    APPROVED_DOWNSTREAM_STATUS_INPUT_VALUES,
    APPROVED_DOWNSTREAM_STATUS_OUTPUT_VALUES,
    APPROVED_INPUT_ARTIFACT_TYPE,
    APPROVED_OUTPUT_ARTIFACT_TYPE,
    FORBIDDEN_INTERNAL_FIELDS,
    REQUIRED_ADAPTER_PACKET_KEYS,
    REQUIRED_RUNTIME_MODE_KEYS,
    REQUIRED_WEIGHT_KEYS,
)


class ChildCoreDeliveryError(ValueError):
    """Raised when Stage 77 child-core delivery validation fails."""


def _as_dict(value) -> dict:
    return value if isinstance(value, dict) else {}


def _as_list(value) -> list:
    return value if isinstance(value, list) else []


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise ChildCoreDeliveryError(message)


def _validate_no_forbidden_fields(packet: dict) -> None:
    leaked = FORBIDDEN_INTERNAL_FIELDS.intersection(packet.keys())
    _assert(not leaked, f"forbidden internal fields present: {sorted(leaked)}")


def validate_child_core_adapter_packet(adapter_packet: dict) -> None:
    _assert(isinstance(adapter_packet, dict), "child_core_adapter_packet must be a dict")
    _assert(
        adapter_packet.get("artifact_type") == APPROVED_INPUT_ARTIFACT_TYPE,
        f"artifact_type must be {APPROVED_INPUT_ARTIFACT_TYPE}",
    )
    _assert(adapter_packet.get("sealed") is True, "child_core_adapter_packet must be sealed")

    missing_keys = REQUIRED_ADAPTER_PACKET_KEYS.difference(adapter_packet.keys())
    _assert(not missing_keys, f"missing adapter packet keys: {sorted(missing_keys)}")

    target_core = adapter_packet.get("target_core")
    _assert(
        target_core in APPROVED_CHILD_CORE_TARGETS,
        f"target_core must be one of {sorted(APPROVED_CHILD_CORE_TARGETS)}",
    )

    target_meta = APPROVED_CHILD_CORE_TARGETS[target_core]
    _assert(
        adapter_packet.get("adapter_class") == target_meta["adapter_class"],
        "adapter_class does not match approved registry value",
    )
    _assert(
        adapter_packet.get("target_surface_class") == target_meta["target_surface_class"],
        "target_surface_class does not match approved registry value",
    )

    _assert(
        adapter_packet.get("adapter_status") in APPROVED_ADAPTER_STATUS_VALUES,
        f"adapter_status must be one of {sorted(APPROVED_ADAPTER_STATUS_VALUES)}",
    )
    _assert(
        adapter_packet.get("downstream_status") in APPROVED_DOWNSTREAM_STATUS_INPUT_VALUES,
        "invalid downstream_status for delivery intake",
    )

    runtime_mode = _as_dict(adapter_packet.get("runtime_mode"))
    missing_runtime_mode = REQUIRED_RUNTIME_MODE_KEYS.difference(runtime_mode.keys())
    _assert(not missing_runtime_mode, f"missing runtime_mode keys: {sorted(missing_runtime_mode)}")

    combined_weights = _as_dict(adapter_packet.get("combined_weights"))
    missing_weights = REQUIRED_WEIGHT_KEYS.difference(combined_weights.keys())
    _assert(not missing_weights, f"missing combined_weights keys: {sorted(missing_weights)}")

    for key in REQUIRED_WEIGHT_KEYS:
        value = combined_weights.get(key)
        _assert(isinstance(value, (int, float)), f"combined_weights.{key} must be numeric")
        _assert(0.0 <= float(value) <= 1.0, f"combined_weights.{key} must be between 0.0 and 1.0")

    _assert(isinstance(adapter_packet.get("adapter_payload"), dict), "adapter_payload must be a dict")
    _validate_no_forbidden_fields(adapter_packet)


def _build_market_analyzer_delivery_payload(adapter_packet: dict) -> dict:
    payload = deepcopy(_as_dict(adapter_packet.get("adapter_payload")))

    market_regime = _as_dict(payload.get("market_regime"))
    event_context = _as_dict(payload.get("event_context"))
    watchlist = _as_dict(payload.get("watchlist"))
    rebound_validation = _as_dict(payload.get("rebound_validation"))
    recommendations = _as_dict(payload.get("recommendations"))
    approval_gate = _as_dict(payload.get("approval_gate"))
    receipt_trace = _as_dict(payload.get("receipt_trace"))

    recommendation_items = _as_list(recommendations.get("items"))
    delivery_symbols = [
        item.get("symbol")
        for item in recommendation_items
        if isinstance(item, dict) and isinstance(item.get("symbol"), str) and item.get("symbol")
    ]

    return {
        "delivery_summary": {
            "target_core": adapter_packet.get("target_core"),
            "delivery_class": APPROVED_CHILD_CORE_TARGETS["market_analyzer_v1"]["delivery_class"],
            "execution_status": payload.get("execution_status"),
            "runtime_error": adapter_packet.get("runtime_error"),
            "recommendation_count": recommendations.get("recommendation_count", len(recommendation_items)),
            "recommendation_symbols": delivery_symbols,
            "advisory_only": True,
            "human_approval_required": True,
            "execution_allowed": False,
        },
        "market_context": {
            "regime": market_regime.get("regime"),
            "trade_posture": market_regime.get("trade_posture"),
            "trade_allowed": market_regime.get("trade_allowed"),
            "volatility_level": market_regime.get("volatility_level"),
            "liquidity_level": market_regime.get("liquidity_level"),
            "stress_level": market_regime.get("stress_level"),
        },
        "event_context": {
            "event_id": event_context.get("event_id"),
            "event_type": event_context.get("event_type"),
            "shock_confirmed": event_context.get("shock_confirmed"),
            "propagation_speed": event_context.get("propagation_speed"),
            "ripple_depth": event_context.get("ripple_depth"),
        },
        "watchlist": {
            "items": watchlist.get("items", []),
            "filtered_count": watchlist.get("filtered_count", 0),
            "rejected_count": watchlist.get("rejected_count", 0),
            "allowed_sectors": watchlist.get("allowed_sectors", []),
        },
        "rebound_validation": {
            "validated_candidates": rebound_validation.get("validated_candidates", []),
            "rejected_candidates": rebound_validation.get("rejected_candidates", []),
            "validated_count": rebound_validation.get("validated_count", 0),
            "rejected_count": rebound_validation.get("rejected_count", 0),
        },
        "recommendations": {
            "items": recommendation_items,
            "recommendation_count": recommendations.get("recommendation_count", len(recommendation_items)),
            "approval_gate": recommendations.get("approval_gate"),
            "execution_allowed": False,
        },
        "approval_gate": {
            "approval_type": approval_gate.get("approval_type"),
            "recommendation_count": approval_gate.get("recommendation_count", 0),
            "execution_allowed": False,
            "trace_reference": approval_gate.get("trace_reference"),
        },
        "receipt_trace": {
            "upstream_receipt": receipt_trace.get("upstream_receipt"),
            "trace": receipt_trace.get("trace", {}),
        },
    }


def _build_rejected_delivery_payload(adapter_packet: dict) -> dict:
    return {
        "delivery_summary": {
            "target_core": adapter_packet.get("target_core"),
            "delivery_class": APPROVED_CHILD_CORE_TARGETS[adapter_packet["target_core"]]["delivery_class"],
            "execution_status": "rejected",
            "runtime_error": adapter_packet.get("runtime_error"),
            "recommendation_count": 0,
            "recommendation_symbols": [],
            "advisory_only": True,
            "human_approval_required": True,
            "execution_allowed": False,
        },
        "market_context": {},
        "event_context": {},
        "watchlist": {
            "items": [],
            "filtered_count": 0,
            "rejected_count": 0,
            "allowed_sectors": [],
        },
        "rebound_validation": {
            "validated_candidates": [],
            "rejected_candidates": [],
            "validated_count": 0,
            "rejected_count": 0,
        },
        "recommendations": {
            "items": [],
            "recommendation_count": 0,
            "approval_gate": None,
            "execution_allowed": False,
        },
        "approval_gate": {
            "approval_type": None,
            "recommendation_count": 0,
            "execution_allowed": False,
            "trace_reference": None,
        },
        "receipt_trace": {},
    }


def build_child_core_delivery_packet(adapter_packet: dict) -> dict:
    validate_child_core_adapter_packet(adapter_packet)

    target_core = adapter_packet["target_core"]
    target_meta = APPROVED_CHILD_CORE_TARGETS[target_core]

    adapter_status = adapter_packet.get("adapter_status")
    delivery_status = "delivered" if adapter_status == "adapted" else "rejected"
    downstream_status = (
        "ready_for_target_consumer"
        if adapter_status == "adapted"
        else "delivery_rejected"
    )

    _assert(
        delivery_status in APPROVED_DELIVERY_STATUS_VALUES,
        "invalid delivery_status during packet construction",
    )
    _assert(
        downstream_status in APPROVED_DOWNSTREAM_STATUS_OUTPUT_VALUES,
        "invalid downstream_status during delivery construction",
    )

    if target_core == "market_analyzer_v1":
        if adapter_status == "adapted":
            delivery_payload = _build_market_analyzer_delivery_payload(adapter_packet)
        else:
            delivery_payload = _build_rejected_delivery_payload(adapter_packet)
    else:
        raise ChildCoreDeliveryError(f"no delivery mapping implemented for target_core={target_core}")

    delivery_packet_id = f"CCDP-{uuid4().hex[:16].upper()}"

    return {
        "artifact_type": APPROVED_OUTPUT_ARTIFACT_TYPE,
        "sealed": True,
        "delivery_packet_id": delivery_packet_id,
        "source_artifact_type": APPROVED_INPUT_ARTIFACT_TYPE,
        "source_lineage": {
            "adapter_packet_id": adapter_packet.get("adapter_packet_id"),
            "source_lineage": adapter_packet.get("source_lineage"),
        },
        "target_core": target_core,
        "delivery_class": target_meta["delivery_class"],
        "target_surface_class": target_meta["target_surface_class"],
        "delivery_status": delivery_status,
        "downstream_status": downstream_status,
        "runtime_mode": deepcopy(adapter_packet.get("runtime_mode", {})),
        "combined_weights": deepcopy(adapter_packet.get("combined_weights", {})),
        "delivery_payload": delivery_payload,
        "runtime_error": adapter_packet.get("runtime_error"),
        "receipt": {
            "receipt_type": "child_core_delivery_surface_receipt",
            "target_core": target_core,
            "delivery_packet_id": delivery_packet_id,
        },
    }