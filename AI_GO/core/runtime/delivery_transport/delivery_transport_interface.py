from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from .delivery_transport_policy import (
    INTERNAL_FIELD_NAMES,
    REQUIRED_ACK_INDEX_FIELDS,
    REQUIRED_TRANSPORT_ENVELOPE_FIELDS,
    TRUE_RESULT_VALUES,
)
from .delivery_transport_registry import (
    ALLOWED_ACK_INDEX_TYPES,
    ALLOWED_EXECUTION_MODES,
    ALLOWED_PAYLOAD_CLASSES,
    ALLOWED_ROUTE_CLASSES,
    ALLOWED_TRANSPORT_ENVELOPE_TYPES,
)


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _reject(reason: str) -> Dict[str, Any]:
    return {
        "status": "rejected",
        "reason": reason,
    }


def _contains_internal_fields(payload: Dict[str, Any]) -> bool:
    return any(field in INTERNAL_FIELD_NAMES for field in payload.keys())


def _validate_required_fields(payload: Dict[str, Any], required_fields: set[str], prefix: str) -> Dict[str, Any] | None:
    for field in sorted(required_fields):
        if field not in payload:
            return _reject(f"missing_{prefix}_field:{field}")
    return None


def _transport_permission(ack_index: Dict[str, Any]) -> bool:
    if ack_index.get("acknowledgement_registered") is not True:
        return False

    if ack_index.get("result") not in TRUE_RESULT_VALUES:
        return False

    if ack_index.get("payload_class") not in ALLOWED_PAYLOAD_CLASSES:
        return False

    if ack_index.get("route_class") not in ALLOWED_ROUTE_CLASSES:
        return False

    if ack_index.get("execution_mode") not in ALLOWED_EXECUTION_MODES:
        return False

    return True


def create_delivery_transport_envelope(ack_index: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(ack_index, dict):
        return _reject("invalid_ack_index_payload")

    if _contains_internal_fields(ack_index):
        return _reject("internal_field_leakage")

    ack_validation = _validate_required_fields(
        payload=ack_index,
        required_fields=REQUIRED_ACK_INDEX_FIELDS,
        prefix="ack_index",
    )
    if ack_validation is not None:
        return ack_validation

    if ack_index.get("ack_index_type") not in ALLOWED_ACK_INDEX_TYPES:
        return _reject("unapproved_ack_index_type")

    if ack_index.get("payload_class") not in ALLOWED_PAYLOAD_CLASSES:
        return _reject("invalid_payload_class")

    if ack_index.get("route_class") not in ALLOWED_ROUTE_CLASSES:
        return _reject("invalid_route_class")

    if ack_index.get("execution_mode") not in ALLOWED_EXECUTION_MODES:
        return _reject("invalid_execution_mode")

    envelope = {
        "transport_envelope_id": f"TE-{ack_index['ack_index_id']}",
        "transport_envelope_type": "delivery_transport_envelope_v1",
        "timestamp": _utc_timestamp(),
        "summary": ack_index["summary"],
        "result": ack_index["result"],
        "ack_index_ref": ack_index["ack_index_id"],
        "ack_index_type": ack_index["ack_index_type"],
        "delivery_receipt_ref": ack_index["delivery_receipt_ref"],
        "delivery_index_ref": ack_index["delivery_index_ref"],
        "dispatch_manifest_ref": ack_index["dispatch_manifest_ref"],
        "bundle_ref": ack_index["bundle_ref"],
        "report_count": ack_index["report_count"],
        "payload_class": ack_index["payload_class"],
        "route_class": ack_index["route_class"],
        "execution_mode": ack_index["execution_mode"],
        "transport_permitted": _transport_permission(ack_index),
    }

    envelope_validation = _validate_required_fields(
        payload=envelope,
        required_fields=REQUIRED_TRANSPORT_ENVELOPE_FIELDS,
        prefix="transport_envelope",
    )
    if envelope_validation is not None:
        return envelope_validation

    if envelope["transport_envelope_type"] not in ALLOWED_TRANSPORT_ENVELOPE_TYPES:
        return _reject("invalid_transport_envelope_type")

    return {
        "status": "ok",
        "transport_envelope": envelope,
    }