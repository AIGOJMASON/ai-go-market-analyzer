from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from .escalation_outcome_policy import (
    INTERNAL_FIELD_NAMES,
    REQUIRED_ESCALATION_EXECUTION_RESULT_FIELDS,
    REQUIRED_ESCALATION_OUTCOME_RECEIPT_FIELDS,
)
from .escalation_outcome_registry import (
    ALLOWED_ESCALATION_ADAPTER_CLASSES,
    ALLOWED_ESCALATION_CLASSES,
    ALLOWED_ESCALATION_EXECUTION_RESULT_TYPES,
    ALLOWED_ESCALATION_OUTCOME_RECEIPT_TYPES,
    ALLOWED_ESCALATION_ROUTES,
    ALLOWED_EXECUTION_MODES,
    ALLOWED_PAYLOAD_CLASSES,
    ALLOWED_RETRY_ADAPTER_CLASSES,
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


def create_escalation_outcome_receipt(
    escalation_execution_result: Dict[str, Any],
) -> Dict[str, Any]:
    if not isinstance(escalation_execution_result, dict):
        return _reject("invalid_escalation_execution_result_payload")

    if _contains_internal_fields(escalation_execution_result):
        return _reject("internal_field_leakage")

    validation = _validate_required_fields(
        payload=escalation_execution_result,
        required_fields=REQUIRED_ESCALATION_EXECUTION_RESULT_FIELDS,
        prefix="escalation_execution_result",
    )
    if validation is not None:
        return validation

    if (
        escalation_execution_result.get("escalation_execution_result_type")
        not in ALLOWED_ESCALATION_EXECUTION_RESULT_TYPES
    ):
        return _reject("unapproved_escalation_execution_result_type")

    if escalation_execution_result.get("payload_class") not in ALLOWED_PAYLOAD_CLASSES:
        return _reject("invalid_payload_class")

    if escalation_execution_result.get("route_class") not in ALLOWED_ROUTE_CLASSES:
        return _reject("invalid_route_class")

    if escalation_execution_result.get("execution_mode") not in ALLOWED_EXECUTION_MODES:
        return _reject("invalid_execution_mode")

    if (
        escalation_execution_result.get("source_adapter_class")
        not in ALLOWED_SOURCE_ADAPTER_CLASSES
    ):
        return _reject("invalid_source_adapter_class")

    if (
        escalation_execution_result.get("retry_adapter_class")
        not in ALLOWED_RETRY_ADAPTER_CLASSES
    ):
        return _reject("invalid_retry_adapter_class")

    if (
        escalation_execution_result.get("escalation_adapter_class")
        not in ALLOWED_ESCALATION_ADAPTER_CLASSES
    ):
        return _reject("invalid_escalation_adapter_class")

    if (
        escalation_execution_result.get("escalation_class")
        not in ALLOWED_ESCALATION_CLASSES
    ):
        return _reject("invalid_escalation_class")

    if (
        escalation_execution_result.get("escalation_route")
        not in ALLOWED_ESCALATION_ROUTES
    ):
        return _reject("invalid_escalation_route")

    receipt = {
        "escalation_outcome_receipt_id": (
            f"EOR-{escalation_execution_result['escalation_execution_id']}"
        ),
        "escalation_outcome_receipt_type": "escalation_outcome_receipt_v1",
        "timestamp": _utc_timestamp(),
        "summary": escalation_execution_result["summary"],
        "result": escalation_execution_result["result"],
        "escalation_execution_ref": escalation_execution_result["escalation_execution_id"],
        "escalation_execution_result_type": escalation_execution_result[
            "escalation_execution_result_type"
        ],
        "escalation_decision_ref": escalation_execution_result["escalation_decision_ref"],
        "source_receipt_ref": escalation_execution_result["source_receipt_ref"],
        "source_receipt_type": escalation_execution_result["source_receipt_type"],
        "payload_class": escalation_execution_result["payload_class"],
        "route_class": escalation_execution_result["route_class"],
        "execution_mode": escalation_execution_result["execution_mode"],
        "source_adapter_class": escalation_execution_result["source_adapter_class"],
        "retry_adapter_class": escalation_execution_result["retry_adapter_class"],
        "escalation_class": escalation_execution_result["escalation_class"],
        "escalation_route": escalation_execution_result["escalation_route"],
        "escalation_adapter_class": escalation_execution_result["escalation_adapter_class"],
        "escalation_attempted": escalation_execution_result["escalation_attempted"],
        "escalation_permitted": escalation_execution_result["escalation_permitted"],
    }

    validation = _validate_required_fields(
        payload=receipt,
        required_fields=REQUIRED_ESCALATION_OUTCOME_RECEIPT_FIELDS,
        prefix="escalation_outcome_receipt",
    )
    if validation is not None:
        return validation

    if (
        receipt["escalation_outcome_receipt_type"]
        not in ALLOWED_ESCALATION_OUTCOME_RECEIPT_TYPES
    ):
        return _reject("invalid_escalation_outcome_receipt_type")

    return {
        "status": "ok",
        "escalation_outcome_receipt": receipt,
    }