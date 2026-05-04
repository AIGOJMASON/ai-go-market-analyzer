from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


ALLOWED_UPSTREAM_ARTIFACT_TYPES = {
    "market_case_record",
    "market_regime_record",
    "event_propagation_record",
    "necessity_filtered_candidate_set",
    "rebound_validation_record",
    "receipt_trace_packet",
    "approval_request_packet",
    "research_packet",
    "pm_decision_packet",
    "refinement_conditioning_packet",
}

REJECTED_SOURCES = {
    "raw_research_core_output",
    "user_direct_input",
    "unverified_external_feed",
}


class IngressValidationError(Exception):
    """Raised when upstream ingress is invalid for market_analyzer_v1."""


def _require_field(obj: Dict[str, Any], field_name: str) -> None:
    if field_name not in obj:
        raise IngressValidationError(f"missing required field: {field_name}")


def _validate_receipt(packet: Dict[str, Any]) -> None:
    receipt = packet.get("receipt") or packet.get("seal") or packet.get("provenance")
    if not receipt:
        raise IngressValidationError("missing receipt/seal/provenance on ingress packet")


def _validate_source(packet: Dict[str, Any]) -> None:
    source = packet.get("source")
    if source in REJECTED_SOURCES:
        raise IngressValidationError(f"rejected ingress source: {source}")


def _validate_artifact_type(packet: Dict[str, Any]) -> None:
    artifact_type = packet.get("artifact_type")
    if artifact_type not in ALLOWED_UPSTREAM_ARTIFACT_TYPES:
        raise IngressValidationError(f"unsupported artifact_type: {artifact_type}")


def _validate_dispatch(packet: Dict[str, Any]) -> None:
    dispatched_by = packet.get("dispatched_by")
    target_core = packet.get("target_core")
    if dispatched_by != "PM_CORE":
        raise IngressValidationError("ingress must be dispatched by PM_CORE")
    if target_core != "market_analyzer_v1":
        raise IngressValidationError("ingress target_core mismatch")


def _validate_payload(packet: Dict[str, Any]) -> None:
    payload = packet.get("payload")
    if not isinstance(payload, dict):
        raise IngressValidationError("payload must be a dict")


def _extract_candidates(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    candidates = payload.get("candidates", [])
    if candidates is None:
        return []
    if not isinstance(candidates, list):
        raise IngressValidationError("payload.candidates must be a list")
    normalized: List[Dict[str, Any]] = []
    for item in candidates:
        if not isinstance(item, dict):
            raise IngressValidationError("each candidate must be a dict")
        normalized.append(deepcopy(item))
    return normalized


def process_ingress(packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize and validate upstream ingress for market_analyzer_v1.

    This child core accepts only PM_CORE-dispatched, sealed, structured packets.
    """
    if not isinstance(packet, dict):
        raise IngressValidationError("ingress packet must be a dict")

    _require_field(packet, "artifact_type")
    _require_field(packet, "payload")
    _require_field(packet, "dispatched_by")
    _require_field(packet, "target_core")

    _validate_dispatch(packet)
    _validate_artifact_type(packet)
    _validate_payload(packet)
    _validate_receipt(packet)
    _validate_source(packet)

    payload = deepcopy(packet["payload"])
    candidates = _extract_candidates(payload)

    normalized = {
        "core_id": "market_analyzer_v1",
        "ingress_valid": True,
        "artifact_type": packet["artifact_type"],
        "dispatch_id": packet.get("dispatch_id"),
        "source": packet.get("source", "validated_upstream"),
        "receipt": deepcopy(packet.get("receipt") or packet.get("seal") or packet.get("provenance")),
        "conditioning": deepcopy(payload.get("conditioning", {})),
        "market_context": deepcopy(payload.get("market_context", {})),
        "event": deepcopy(payload.get("event", {})),
        "macro_bias": deepcopy(payload.get("macro_bias", {})),
        "candidates": candidates,
        "notes": deepcopy(payload.get("notes", [])),
    }

    return normalized