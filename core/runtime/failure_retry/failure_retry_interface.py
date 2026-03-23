from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Tuple

from .failure_retry_policy import (
    INTERNAL_FIELD_NAMES,
    REQUIRED_DELIVERY_OUTCOME_RECEIPT_FIELDS,
    REQUIRED_FAILURE_RETRY_DECISION_FIELDS,
)
from .failure_retry_registry import (
    ALLOWED_ADAPTER_CLASSES,
    ALLOWED_DELIVERY_OUTCOME_RECEIPT_TYPES,
    ALLOWED_EXECUTION_MODES,
    ALLOWED_FAILURE_RETRY_DECISION_TYPES,
    ALLOWED_OUTCOME_RESULTS,
    ALLOWED_PAYLOAD_CLASSES,
    ALLOWED_ROUTE_CLASSES,
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


def _classify_outcome(result: str) -> Tuple[bool, bool, bool, str]:
    if result == "executed":
        return True, False, False, "Execution completed successfully. Outcome is terminal."
    if result == "denied":
        return False, True, False, "Execution was denied. Retry may be permitted later."
    if result == "failed":
        return False, True, True, "Execution failed. Retry may be permitted and escalation is suggested."
    return True, False, False, "Outcome classified as terminal under current failure governance policy."


def create_failure_retry_decision(
    delivery_outcome_receipt: Dict[str, Any],
) -> Dict[str, Any]:
    if not isinstance(delivery_outcome_receipt, dict):
        return _reject("invalid_delivery_outcome_receipt_payload")

    if _contains_internal_fields(delivery_outcome_receipt):
        return _reject("internal_field_leakage")

    receipt_validation = _validate_required_fields(
        payload=delivery_outcome_receipt,
        required_fields=REQUIRED_DELIVERY_OUTCOME_RECEIPT_FIELDS,
        prefix="delivery_outcome_receipt",
    )
    if receipt_validation is not None:
        return receipt_validation

    if (
        delivery_outcome_receipt.get("delivery_outcome_receipt_type")
        not in ALLOWED_DELIVERY_OUTCOME_RECEIPT_TYPES
    ):
        return _reject("unapproved_delivery_outcome_receipt_type")

    if delivery_outcome_receipt.get("payload_class") not in ALLOWED_PAYLOAD_CLASSES:
        return _reject("invalid_payload_class")

    if delivery_outcome_receipt.get("route_class") not in ALLOWED_ROUTE_CLASSES:
        return _reject("invalid_route_class")

    if delivery_outcome_receipt.get("execution_mode") not in ALLOWED_EXECUTION_MODES:
        return _reject("invalid_execution_mode")

    if delivery_outcome_receipt.get("adapter_class") not in ALLOWED_ADAPTER_CLASSES:
        return _reject("invalid_adapter_class")

    if delivery_outcome_receipt.get("result") not in ALLOWED_OUTCOME_RESULTS:
        return _reject("invalid_outcome_result")

    terminal, retry_eligible, escalation_suggested, summary = _classify_outcome(
        delivery_outcome_receipt["result"]
    )

    decision = {
        "failure_retry_decision_id": (
            f"FRD-{delivery_outcome_receipt['delivery_outcome_receipt_id']}"
        ),
        "failure_retry_decision_type": "failure_retry_decision_v1",
        "timestamp": _utc_timestamp(),
        "summary": summary,
        "result": delivery_outcome_receipt["result"],
        "delivery_outcome_receipt_ref": delivery_outcome_receipt[
            "delivery_outcome_receipt_id"
        ],
        "transport_execution_ref": delivery_outcome_receipt["transport_execution_ref"],
        "transport_envelope_ref": delivery_outcome_receipt["transport_envelope_ref"],
        "ack_index_ref": delivery_outcome_receipt["ack_index_ref"],
        "payload_class": delivery_outcome_receipt["payload_class"],
        "route_class": delivery_outcome_receipt["route_class"],
        "execution_mode": delivery_outcome_receipt["execution_mode"],
        "adapter_class": delivery_outcome_receipt["adapter_class"],
        "execution_attempted": delivery_outcome_receipt["execution_attempted"],
        "execution_permitted": delivery_outcome_receipt["execution_permitted"],
        "terminal": terminal,
        "retry_eligible": retry_eligible,
        "escalation_suggested": escalation_suggested,
    }

    decision_validation = _validate_required_fields(
        payload=decision,
        required_fields=REQUIRED_FAILURE_RETRY_DECISION_FIELDS,
        prefix="failure_retry_decision",
    )
    if decision_validation is not None:
        return decision_validation

    if (
        decision["failure_retry_decision_type"]
        not in ALLOWED_FAILURE_RETRY_DECISION_TYPES
    ):
        return _reject("invalid_failure_retry_decision_type")

    return {
        "status": "ok",
        "failure_retry_decision": decision,
    }