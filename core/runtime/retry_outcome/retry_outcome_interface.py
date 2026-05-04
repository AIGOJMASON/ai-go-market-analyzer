from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from .retry_outcome_policy import (
    INTERNAL_FIELD_NAMES,
    REQUIRED_RETRY_EXECUTION_RESULT_FIELDS,
    REQUIRED_RETRY_OUTCOME_RECEIPT_FIELDS,
)
from .retry_outcome_registry import (
    ALLOWED_EXECUTION_MODES,
    ALLOWED_PAYLOAD_CLASSES,
    ALLOWED_RETRY_ADAPTER_CLASSES,
    ALLOWED_RETRY_EXECUTION_RESULT_TYPES,
    ALLOWED_RETRY_OUTCOME_RECEIPT_TYPES,
    ALLOWED_ROUTE_CLASSES,
    ALLOWED_SOURCE_ADAPTER_CLASSES,
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


def create_retry_outcome_receipt(
    retry_execution_result: Dict[str, Any],
) -> Dict[str, Any]:
    if not isinstance(retry_execution_result, dict):
        return _reject("invalid_retry_execution_result_payload")

    if _contains_internal_fields(retry_execution_result):
        return _reject("internal_field_leakage")

    result_validation = _validate_required_fields(
        payload=retry_execution_result,
        required_fields=REQUIRED_RETRY_EXECUTION_RESULT_FIELDS,
        prefix="retry_execution_result",
    )
    if result_validation is not None:
        return result_validation

    if (
        retry_execution_result.get("retry_execution_result_type")
        not in ALLOWED_RETRY_EXECUTION_RESULT_TYPES
    ):
        return _reject("unapproved_retry_execution_result_type")

    if retry_execution_result.get("payload_class") not in ALLOWED_PAYLOAD_CLASSES:
        return _reject("invalid_payload_class")

    if retry_execution_result.get("route_class") not in ALLOWED_ROUTE_CLASSES:
        return _reject("invalid_route_class")

    if retry_execution_result.get("execution_mode") not in ALLOWED_EXECUTION_MODES:
        return _reject("invalid_execution_mode")

    if (
        retry_execution_result.get("source_adapter_class")
        not in ALLOWED_SOURCE_ADAPTER_CLASSES
    ):
        return _reject("invalid_source_adapter_class")

    if (
        retry_execution_result.get("retry_adapter_class")
        not in ALLOWED_RETRY_ADAPTER_CLASSES
    ):
        return _reject("invalid_retry_adapter_class")

    receipt = {
        "retry_outcome_receipt_id": (
            f"ROR-{retry_execution_result['retry_execution_id']}"
        ),
        "retry_outcome_receipt_type": "retry_outcome_receipt_v1",
        "timestamp": _utc_timestamp(),
        "summary": retry_execution_result["summary"],
        "result": retry_execution_result["result"],
        "retry_execution_ref": retry_execution_result["retry_execution_id"],
        "retry_execution_result_type": retry_execution_result[
            "retry_execution_result_type"
        ],
        "failure_retry_decision_ref": retry_execution_result[
            "failure_retry_decision_ref"
        ],
        "delivery_outcome_receipt_ref": retry_execution_result[
            "delivery_outcome_receipt_ref"
        ],
        "transport_execution_ref": retry_execution_result["transport_execution_ref"],
        "transport_envelope_ref": retry_execution_result["transport_envelope_ref"],
        "ack_index_ref": retry_execution_result["ack_index_ref"],
        "payload_class": retry_execution_result["payload_class"],
        "route_class": retry_execution_result["route_class"],
        "execution_mode": retry_execution_result["execution_mode"],
        "source_adapter_class": retry_execution_result["source_adapter_class"],
        "retry_adapter_class": retry_execution_result["retry_adapter_class"],
        "retry_attempted": retry_execution_result["retry_attempted"],
        "retry_permitted": retry_execution_result["retry_permitted"],
        "terminal": retry_execution_result["terminal"],
        "retry_eligible": retry_execution_result["retry_eligible"],
        "escalation_suggested": retry_execution_result["escalation_suggested"],
    }

    receipt_validation = _validate_required_fields(
        payload=receipt,
        required_fields=REQUIRED_RETRY_OUTCOME_RECEIPT_FIELDS,
        prefix="retry_outcome_receipt",
    )
    if receipt_validation is not None:
        return receipt_validation

    if (
        receipt["retry_outcome_receipt_type"]
        not in ALLOWED_RETRY_OUTCOME_RECEIPT_TYPES
    ):
        return _reject("invalid_retry_outcome_receipt_type")

    return {
        "status": "ok",
        "retry_outcome_receipt": receipt,
    }