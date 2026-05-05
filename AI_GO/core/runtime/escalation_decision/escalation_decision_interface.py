from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Tuple

from .escalation_decision_policy import (
    INTERNAL_FIELD_NAMES,
    REQUIRED_DELIVERY_OUTCOME_RECEIPT_FIELDS,
    REQUIRED_ESCALATION_DECISION_FIELDS,
    REQUIRED_RETRY_OUTCOME_RECEIPT_FIELDS,
)
from .escalation_decision_registry import (
    ALLOWED_ESCALATION_CLASSES,
    ALLOWED_ESCALATION_DECISION_TYPES,
    ALLOWED_ESCALATION_ROUTES,
    ALLOWED_EXECUTION_MODES,
    ALLOWED_PAYLOAD_CLASSES,
    ALLOWED_RETRY_ADAPTER_CLASSES,
    ALLOWED_ROUTE_CLASSES,
    ALLOWED_SOURCE_ADAPTER_CLASSES,
    ALLOWED_SOURCE_RECEIPT_TYPES,
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


def _classify_delivery_outcome(result: str) -> Tuple[bool, str, str, str]:
    if result == "executed":
        return False, "none", "none", "Delivery outcome is terminal. Escalation not required."
    if result == "denied":
        return False, "retry_path", "retry_governance", "Delivery outcome denied. Route back through retry governance."
    if result == "failed":
        return True, "operator_review", "operator_queue", "Delivery outcome failed. Escalation to operator review is required."
    return False, "none", "none", "Delivery outcome classified as non-escalating under current policy."


def _classify_retry_outcome(result: str) -> Tuple[bool, str, str, str]:
    if result == "retried":
        return True, "operator_review", "operator_queue", "Retry completed. Escalation to operator review is required."
    if result == "retry_denied":
        return True, "policy_block", "operator_queue", "Retry was denied. Escalation due to policy block is required."
    return False, "none", "none", "Retry outcome classified as non-escalating under current policy."


def create_escalation_decision(source_receipt: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(source_receipt, dict):
        return _reject("invalid_source_receipt_payload")

    if _contains_internal_fields(source_receipt):
        return _reject("internal_field_leakage")

    source_type = (
        source_receipt.get("delivery_outcome_receipt_type")
        or source_receipt.get("retry_outcome_receipt_type")
    )

    if source_type not in ALLOWED_SOURCE_RECEIPT_TYPES:
        return _reject("unapproved_source_receipt_type")

    retry_adapter_class = "none"

    if source_type == "delivery_outcome_receipt_v1":
        validation = _validate_required_fields(
            payload=source_receipt,
            required_fields=REQUIRED_DELIVERY_OUTCOME_RECEIPT_FIELDS,
            prefix="delivery_outcome_receipt",
        )
        if validation is not None:
            return validation

        if source_receipt.get("payload_class") not in ALLOWED_PAYLOAD_CLASSES:
            return _reject("invalid_payload_class")

        if source_receipt.get("route_class") not in ALLOWED_ROUTE_CLASSES:
            return _reject("invalid_route_class")

        if source_receipt.get("execution_mode") not in ALLOWED_EXECUTION_MODES:
            return _reject("invalid_execution_mode")

        source_adapter_class = source_receipt.get("adapter_class")
        if source_adapter_class not in ALLOWED_SOURCE_ADAPTER_CLASSES:
            return _reject("invalid_source_adapter_class")

        escalation_required, escalation_class, escalation_route, summary = _classify_delivery_outcome(
            source_receipt["result"]
        )

        result = source_receipt["result"]
        source_receipt_ref = source_receipt["delivery_outcome_receipt_id"]

    else:
        validation = _validate_required_fields(
            payload=source_receipt,
            required_fields=REQUIRED_RETRY_OUTCOME_RECEIPT_FIELDS,
            prefix="retry_outcome_receipt",
        )
        if validation is not None:
            return validation

        if source_receipt.get("payload_class") not in ALLOWED_PAYLOAD_CLASSES:
            return _reject("invalid_payload_class")

        if source_receipt.get("route_class") not in ALLOWED_ROUTE_CLASSES:
            return _reject("invalid_route_class")

        if source_receipt.get("execution_mode") not in ALLOWED_EXECUTION_MODES:
            return _reject("invalid_execution_mode")

        source_adapter_class = source_receipt.get("source_adapter_class")
        if source_adapter_class not in ALLOWED_SOURCE_ADAPTER_CLASSES:
            return _reject("invalid_source_adapter_class")

        retry_adapter_class = source_receipt.get("retry_adapter_class")
        if retry_adapter_class not in ALLOWED_RETRY_ADAPTER_CLASSES:
            return _reject("invalid_retry_adapter_class")

        escalation_required, escalation_class, escalation_route, summary = _classify_retry_outcome(
            source_receipt["result"]
        )

        result = source_receipt["result"]
        source_receipt_ref = source_receipt["retry_outcome_receipt_id"]

    decision = {
        "escalation_decision_id": f"ED-{source_receipt_ref}",
        "escalation_decision_type": "escalation_decision_v1",
        "timestamp": _utc_timestamp(),
        "summary": summary,
        "result": result,
        "source_receipt_ref": source_receipt_ref,
        "source_receipt_type": source_type,
        "payload_class": source_receipt["payload_class"],
        "route_class": source_receipt["route_class"],
        "execution_mode": source_receipt["execution_mode"],
        "source_adapter_class": source_adapter_class,
        "retry_adapter_class": retry_adapter_class,
        "escalation_required": escalation_required,
        "escalation_class": escalation_class,
        "escalation_route": escalation_route,
    }

    validation = _validate_required_fields(
        payload=decision,
        required_fields=REQUIRED_ESCALATION_DECISION_FIELDS,
        prefix="escalation_decision",
    )
    if validation is not None:
        return validation

    if decision["escalation_decision_type"] not in ALLOWED_ESCALATION_DECISION_TYPES:
        return _reject("invalid_escalation_decision_type")

    if decision["escalation_class"] not in ALLOWED_ESCALATION_CLASSES:
        return _reject("invalid_escalation_class")

    if decision["escalation_route"] not in ALLOWED_ESCALATION_ROUTES:
        return _reject("invalid_escalation_route")

    return {
        "status": "ok",
        "escalation_decision": decision,
    }