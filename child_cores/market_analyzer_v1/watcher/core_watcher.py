from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


REQUIRED_ARTIFACT_KEYS = {
    "market_regime_record",
    "event_propagation_record",
    "necessity_filtered_candidate_set",
    "rebound_validation_record",
    "trade_recommendation_packet",
    "receipt_trace_packet",
    "approval_request_packet",
}


class CoreWatcherError(Exception):
    """Raised when local watcher input is invalid."""


def _validate_required_artifacts(artifacts: Dict[str, Any]) -> List[str]:
    failures: List[str] = []
    for key in sorted(REQUIRED_ARTIFACT_KEYS):
        if key not in artifacts:
            failures.append(f"missing artifact: {key}")
        elif not isinstance(artifacts[key], dict):
            failures.append(f"artifact is not dict: {key}")
    return failures


def _validate_recommendation_packet(packet: Dict[str, Any]) -> List[str]:
    failures: List[str] = []
    if packet.get("artifact_type") != "trade_recommendation_packet":
        failures.append("invalid recommendation artifact_type")
    if packet.get("execution_allowed") is not False:
        failures.append("execution_allowed must be false")
    if packet.get("approval_gate") != "human_trade_approval_record":
        failures.append("approval_gate mismatch")
    if not isinstance(packet.get("recommendations", []), list):
        failures.append("recommendations must be a list")
    return failures


def _validate_trace_packet(packet: Dict[str, Any]) -> List[str]:
    failures: List[str] = []
    if packet.get("artifact_type") != "receipt_trace_packet":
        failures.append("invalid receipt trace artifact_type")
    if not packet.get("upstream_receipt"):
        failures.append("missing upstream receipt")
    if not isinstance(packet.get("trace", {}), dict):
        failures.append("trace must be a dict")
    return failures


def _validate_approval_packet(packet: Dict[str, Any]) -> List[str]:
    failures: List[str] = []
    if packet.get("artifact_type") != "approval_request_packet":
        failures.append("invalid approval request artifact_type")
    if packet.get("approval_type") != "human_trade_approval_record":
        failures.append("approval type mismatch")
    if packet.get("execution_allowed") is not False:
        failures.append("approval request must preserve execution_allowed=false")
    return failures


def verify_runtime_result(runtime_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify required market_analyzer_v1 outputs before continuity is recorded.
    """
    if not isinstance(runtime_result, dict):
        raise CoreWatcherError("runtime_result must be a dict")

    artifacts = runtime_result.get("artifacts")
    if not isinstance(artifacts, dict):
        raise CoreWatcherError("runtime_result.artifacts must be a dict")

    failures: List[str] = []
    failures.extend(_validate_required_artifacts(artifacts))

    if not failures:
        failures.extend(_validate_recommendation_packet(artifacts["trade_recommendation_packet"]))
        failures.extend(_validate_trace_packet(artifacts["receipt_trace_packet"]))
        failures.extend(_validate_approval_packet(artifacts["approval_request_packet"]))

    watcher_passed = len(failures) == 0

    return {
        "core_id": "market_analyzer_v1",
        "artifact_type": "child_core_watcher_result",
        "watcher_passed": watcher_passed,
        "failures": failures,
        "watcher_receipt": None if not watcher_passed else {
            "receipt_type": "child_core_watcher_success_receipt",
            "core_id": "market_analyzer_v1",
            "verified_artifacts": sorted(REQUIRED_ARTIFACT_KEYS),
        },
    }