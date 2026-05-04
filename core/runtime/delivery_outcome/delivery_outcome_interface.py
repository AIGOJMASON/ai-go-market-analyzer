from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from .delivery_outcome_policy import (
    INTERNAL_FIELD_NAMES,
    REQUIRED_DELIVERY_OUTCOME_RECEIPT_FIELDS,
    REQUIRED_TRANSPORT_EXECUTION_RESULT_FIELDS,
)
from .delivery_outcome_registry import (
    ALLOWED_ADAPTER_CLASSES,
    ALLOWED_DELIVERY_OUTCOME_RECEIPT_TYPES,
    ALLOWED_EXECUTION_MODES,
    ALLOWED_PAYLOAD_CLASSES,
    ALLOWED_ROUTE_CLASSES,
    ALLOWED_TRANSPORT_EXECUTION_RESULT_TYPES,
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


def _validate_required_fields(
    payload: Dict[str, Any],
    required_fields: set[str],
    prefix: str,
) -> Dict[str, Any] | None:
    for field in sorted(required_fields):
        if field not in payload:
            return _reject(f"missing_{prefix}_field:{field}")
    return None


def create_delivery_outcome_receipt(
    transport_execution_result: Dict[str, Any],
) -> Dict[str, Any]:
    if not isinstance(transport_execution_result, dict):
        return _reject("invalid_transport_execution_result_payload")

    if _contains_internal_fields(transport_execution_result):
        return _reject("internal_field_leakage")

    execution_validation = _validate_required_fields(
        payload=transport_execution_result,
        required_fields=REQUIRED_TRANSPORT_EXECUTION_RESULT_FIELDS,
        prefix="transport_execution_result",
    )
    if execution_validation is not None:
        return execution_validation

    if (
        transport_execution_result.get("transport_execution_result_type")
        not in ALLOWED_TRANSPORT_EXECUTION_RESULT_TYPES
    ):
        return _reject("unapproved_transport_execution_result_type")

    if transport_execution_result.get("payload_class") not in ALLOWED_PAYLOAD_CLASSES:
        return _reject("invalid_payload_class")

    if transport_execution_result.get("route_class") not in ALLOWED_ROUTE_CLASSES:
        return _reject("invalid_route_class")

    if transport_execution_result.get("execution_mode") not in ALLOWED_EXECUTION_MODES:
        return _reject("invalid_execution_mode")

    if transport_execution_result.get("adapter_class") not in ALLOWED_ADAPTER_CLASSES:
        return _reject("invalid_adapter_class")

    receipt = {
        "delivery_outcome_receipt_id": (
            f"DOR-{transport_execution_result['transport_execution_id']}"
        ),
        "delivery_outcome_receipt_type": "delivery_outcome_receipt_v1",
        "timestamp": _utc_timestamp(),
        "summary": transport_execution_result["summary"],
        "result": transport_execution_result["result"],
        "transport_execution_ref": transport_execution_result["transport_execution_id"],
        "transport_execution_result_type": transport_execution_result[
            "transport_execution_result_type"
        ],
        "transport_envelope_ref": transport_execution_result["transport_envelope_ref"],
        "ack_index_ref": transport_execution_result["ack_index_ref"],
        "payload_class": transport_execution_result["payload_class"],
        "route_class": transport_execution_result["route_class"],
        "execution_mode": transport_execution_result["execution_mode"],
        "adapter_class": transport_execution_result["adapter_class"],
        "execution_attempted": transport_execution_result["execution_attempted"],
        "execution_permitted": transport_execution_result["execution_permitted"],
    }

    receipt_validation = _validate_required_fields(
        payload=receipt,
        required_fields=REQUIRED_DELIVERY_OUTCOME_RECEIPT_FIELDS,
        prefix="delivery_outcome_receipt",
    )
    if receipt_validation is not None:
        return receipt_validation

    if (
        receipt["delivery_outcome_receipt_type"]
        not in ALLOWED_DELIVERY_OUTCOME_RECEIPT_TYPES
    ):
        return _reject("invalid_delivery_outcome_receipt_type")

    return {
        "status": "ok",
        "delivery_outcome_receipt": receipt,
    }