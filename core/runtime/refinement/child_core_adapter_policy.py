from __future__ import annotations

from copy import deepcopy
from uuid import uuid4

from AI_GO.core.runtime.refinement.child_core_adapter_registry import (
    APPROVED_ADAPTER_STATUS_VALUES,
    APPROVED_CHILD_CORE_TARGETS,
    APPROVED_DOWNSTREAM_STATUS_INPUT_VALUES,
    APPROVED_DOWNSTREAM_STATUS_OUTPUT_VALUES,
    APPROVED_EXECUTION_STATUS_VALUES,
    APPROVED_INPUT_ARTIFACT_TYPE,
    APPROVED_OUTPUT_ARTIFACT_TYPE,
    FORBIDDEN_INTERNAL_FIELDS,
    REQUIRED_EXECUTION_RESULT_KEYS,
    REQUIRED_RUNTIME_MODE_KEYS,
    REQUIRED_WEIGHT_KEYS,
)


class ChildCoreAdapterError(ValueError):
    """Raised when Stage 76 child-core adapter validation fails."""


def _as_dict(value) -> dict:
    return value if isinstance(value, dict) else {}


def _as_list(value) -> list:
    return value if isinstance(value, list) else []


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise ChildCoreAdapterError(message)


def _validate_no_forbidden_fields(result: dict) -> None:
    leaked = FORBIDDEN_INTERNAL_FIELDS.intersection(result.keys())
    _assert(not leaked, f"forbidden internal fields present: {sorted(leaked)}")


def validate_child_core_execution_result(execution_result: dict) -> None:
    _assert(isinstance(execution_result, dict), "child_core_execution_result must be a dict")
    _assert(
        execution_result.get("artifact_type") == APPROVED_INPUT_ARTIFACT_TYPE,
        f"artifact_type must be {APPROVED_INPUT_ARTIFACT_TYPE}",
    )
    _assert(execution_result.get("sealed") is True, "child_core_execution_result must be sealed")

    missing_keys = REQUIRED_EXECUTION_RESULT_KEYS.difference(execution_result.keys())
    _assert(not missing_keys, f"missing execution result keys: {sorted(missing_keys)}")

    target_core = execution_result.get("target_core")
    _assert(
        target_core in APPROVED_CHILD_CORE_TARGETS,
        f"target_core must be one of {sorted(APPROVED_CHILD_CORE_TARGETS)}",
    )

    execution_status = execution_result.get("execution_status")
    _assert(
        execution_status in APPROVED_EXECUTION_STATUS_VALUES,
        f"execution_status must be one of {sorted(APPROVED_EXECUTION_STATUS_VALUES)}",
    )

    downstream_status = execution_result.get("downstream_status")
    _assert(
        downstream_status in APPROVED_DOWNSTREAM_STATUS_INPUT_VALUES,
        "invalid downstream_status for adapter intake",
    )

    runtime_mode = _as_dict(execution_result.get("runtime_mode"))
    missing_runtime_mode = REQUIRED_RUNTIME_MODE_KEYS.difference(runtime_mode.keys())
    _assert(not missing_runtime_mode, f"missing runtime_mode keys: {sorted(missing_runtime_mode)}")

    combined_weights = _as_dict(execution_result.get("combined_weights"))
    missing_weights = REQUIRED_WEIGHT_KEYS.difference(combined_weights.keys())
    _assert(not missing_weights, f"missing combined_weights keys: {sorted(missing_weights)}")

    for key in REQUIRED_WEIGHT_KEYS:
        value = combined_weights.get(key)
        _assert(isinstance(value, (int, float)), f"combined_weights.{key} must be numeric")
        _assert(0.0 <= float(value) <= 1.0, f"combined_weights.{key} must be between 0.0 and 1.0")

    _validate_no_forbidden_fields(execution_result)


def _extract_market_analyzer_artifacts(execution_result: dict) -> dict:
    execution_artifacts = execution_result.get("execution_artifacts")
    if isinstance(execution_artifacts, dict):
        artifacts = execution_artifacts.get("artifacts")
        if isinstance(artifacts, dict):
            return deepcopy(artifacts)
        return deepcopy(execution_artifacts)
    return {}


def _build_market_analyzer_adapter_payload(execution_result: dict) -> dict:
    artifacts = _extract_market_analyzer_artifacts(execution_result)

    market_regime_record = _as_dict(artifacts.get("market_regime_record"))
    event_propagation_record = _as_dict(artifacts.get("event_propagation_record"))
    necessity_filtered_candidate_set = _as_dict(artifacts.get("necessity_filtered_candidate_set"))
    rebound_validation_record = _as_dict(artifacts.get("rebound_validation_record"))
    trade_recommendation_packet = _as_dict(artifacts.get("trade_recommendation_packet"))
    receipt_trace_packet = _as_dict(artifacts.get("receipt_trace_packet"))
    approval_request_packet = _as_dict(artifacts.get("approval_request_packet"))

    recommendations = _as_list(trade_recommendation_packet.get("recommendations"))
    watchlist = _as_list(necessity_filtered_candidate_set.get("filtered_candidates"))

    return {
        "target_core": execution_result.get("target_core"),
        "execution_status": execution_result.get("execution_status"),
        "market_regime": {
            "regime": market_regime_record.get("regime"),
            "trade_posture": market_regime_record.get("trade_posture"),
            "trade_allowed": market_regime_record.get("trade_allowed"),
            "volatility_level": market_regime_record.get("volatility_level"),
            "liquidity_level": market_regime_record.get("liquidity_level"),
            "stress_level": market_regime_record.get("stress_level"),
        },
        "event_context": {
            "event_id": event_propagation_record.get("event_id"),
            "event_type": event_propagation_record.get("event_type"),
            "shock_confirmed": event_propagation_record.get("shock_confirmed"),
            "propagation_speed": event_propagation_record.get("propagation_speed"),
            "ripple_depth": event_propagation_record.get("ripple_depth"),
        },
        "watchlist": {
            "items": watchlist,
            "filtered_count": necessity_filtered_candidate_set.get("filtered_count", 0),
            "rejected_count": necessity_filtered_candidate_set.get("rejected_count", 0),
            "allowed_sectors": necessity_filtered_candidate_set.get("allowed_sectors", []),
        },
        "rebound_validation": {
            "validated_candidates": rebound_validation_record.get("validated_candidates", []),
            "rejected_candidates": rebound_validation_record.get("rejected_candidates", []),
            "validated_count": rebound_validation_record.get("validated_count", 0),
            "rejected_count": rebound_validation_record.get("rejected_count", 0),
        },
        "recommendations": {
            "items": recommendations,
            "recommendation_count": trade_recommendation_packet.get("recommendation_count", len(recommendations)),
            "approval_gate": trade_recommendation_packet.get("approval_gate"),
            "execution_allowed": trade_recommendation_packet.get("execution_allowed"),
        },
        "approval_gate": {
            "approval_type": approval_request_packet.get("approval_type"),
            "recommendation_count": approval_request_packet.get("recommendation_count", 0),
            "execution_allowed": approval_request_packet.get("execution_allowed"),
            "trace_reference": approval_request_packet.get("trace_reference"),
        },
        "receipt_trace": {
            "upstream_receipt": receipt_trace_packet.get("upstream_receipt"),
            "trace": receipt_trace_packet.get("trace", {}),
        },
    }


def build_child_core_adapter_packet(execution_result: dict) -> dict:
    validate_child_core_execution_result(execution_result)

    target_core = execution_result["target_core"]
    target_meta = APPROVED_CHILD_CORE_TARGETS[target_core]
    adapter_class = target_meta["adapter_class"]
    target_surface_class = target_meta["target_surface_class"]

    execution_status = execution_result.get("execution_status")
    adapter_status = "adapted" if execution_status == "succeeded" else "rejected"
    downstream_status = (
        "ready_for_target_surface"
        if execution_status == "succeeded"
        else "adapter_rejected"
    )

    _assert(
        adapter_status in APPROVED_ADAPTER_STATUS_VALUES,
        "invalid adapter_status during packet construction",
    )
    _assert(
        downstream_status in APPROVED_DOWNSTREAM_STATUS_OUTPUT_VALUES,
        "invalid downstream_status during adapter construction",
    )

    if target_core == "market_analyzer_v1":
        adapter_payload = _build_market_analyzer_adapter_payload(execution_result)
    else:
        raise ChildCoreAdapterError(f"no adapter mapping implemented for target_core={target_core}")

    packet_id = f"CCAP-{uuid4().hex[:16].upper()}"

    return {
        "artifact_type": APPROVED_OUTPUT_ARTIFACT_TYPE,
        "sealed": True,
        "adapter_packet_id": packet_id,
        "source_artifact_type": APPROVED_INPUT_ARTIFACT_TYPE,
        "source_lineage": {
            "result_id": execution_result.get("result_id"),
            "source_lineage": execution_result.get("source_lineage"),
        },
        "target_core": target_core,
        "adapter_class": adapter_class,
        "target_surface_class": target_surface_class,
        "adapter_status": adapter_status,
        "downstream_status": downstream_status,
        "runtime_mode": deepcopy(execution_result.get("runtime_mode", {})),
        "combined_weights": deepcopy(execution_result.get("combined_weights", {})),
        "adapter_payload": adapter_payload,
        "runtime_error": execution_result.get("runtime_error"),
        "receipt": {
            "receipt_type": "child_core_adapter_surface_receipt",
            "target_core": target_core,
            "adapter_packet_id": packet_id,
        },
    }