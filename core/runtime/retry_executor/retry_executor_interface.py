from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from .retry_executor_adapters import (
    gated_auto_retry_adapter,
    manual_retry_adapter,
)
from .retry_executor_policy import (
    INTERNAL_FIELD_NAMES,
    REQUIRED_FAILURE_RETRY_DECISION_FIELDS,
    REQUIRED_RETRY_EXECUTION_RESULT_FIELDS,
)
from .retry_executor_registry import (
    ALLOWED_ADAPTER_CLASSES,
    ALLOWED_EXECUTION_MODES,
    ALLOWED_FAILURE_RETRY_DECISION_TYPES,
    ALLOWED_PAYLOAD_CLASSES,
    ALLOWED_RETRY_ADAPTERS,
    ALLOWED_RETRY_EXECUTION_RESULT_TYPES,
    ALLOWED_ROUTE_CLASSES,
    RETRY_EXECUTION_MODE_TO_ADAPTER,
    ROUTE_TO_ALLOWED_RETRY_ADAPTERS,
)


RETRY_ADAPTER_FUNCTIONS = {
    "manual_retry_adapter": manual_retry_adapter,
    "gated_auto_retry_adapter": gated_auto_retry_adapter,
}


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


def _denied_retry_result(decision: Dict[str, Any], retry_adapter_class: str) -> Dict[str, Any]:
    result_payload = {
        "retry_execution_id": f"RTX-{decision['failure_retry_decision_id']}",
        "retry_execution_result_type": "retry_execution_result_v1",
        "timestamp": _utc_timestamp(),
        "summary": "Retry execution denied by retry governance gate.",
        "result": "retry_denied",
        "failure_retry_decision_ref": decision["failure_retry_decision_id"],
        "delivery_outcome_receipt_ref": decision["delivery_outcome_receipt_ref"],
        "transport_execution_ref": decision["transport_execution_ref"],
        "transport_envelope_ref": decision["transport_envelope_ref"],
        "ack_index_ref": decision["ack_index_ref"],
        "payload_class": decision["payload_class"],
        "route_class": decision["route_class"],
        "execution_mode": decision["execution_mode"],
        "source_adapter_class": decision["adapter_class"],
        "retry_adapter_class": retry_adapter_class,
        "retry_attempted": False,
        "retry_permitted": False,
        "terminal": decision["terminal"],
        "retry_eligible": decision["retry_eligible"],
        "escalation_suggested": decision["escalation_suggested"],
    }
    return {
        "status": "ok",
        "retry_execution_result": result_payload,
    }


def execute_retry_decision(failure_retry_decision: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(failure_retry_decision, dict):
        return _reject("invalid_failure_retry_decision_payload")

    if _contains_internal_fields(failure_retry_decision):
        return _reject("internal_field_leakage")

    decision_validation = _validate_required_fields(
        payload=failure_retry_decision,
        required_fields=REQUIRED_FAILURE_RETRY_DECISION_FIELDS,
        prefix="failure_retry_decision",
    )
    if decision_validation is not None:
        return decision_validation

    if (
        failure_retry_decision.get("failure_retry_decision_type")
        not in ALLOWED_FAILURE_RETRY_DECISION_TYPES
    ):
        return _reject("unapproved_failure_retry_decision_type")

    if failure_retry_decision.get("payload_class") not in ALLOWED_PAYLOAD_CLASSES:
        return _reject("invalid_payload_class")

    if failure_retry_decision.get("route_class") not in ALLOWED_ROUTE_CLASSES:
        return _reject("invalid_route_class")

    execution_mode = failure_retry_decision.get("execution_mode")
    if execution_mode not in ALLOWED_EXECUTION_MODES:
        return _reject("invalid_execution_mode")

    source_adapter_class = failure_retry_decision.get("adapter_class")
    if source_adapter_class not in ALLOWED_ADAPTER_CLASSES:
        return _reject("invalid_adapter_class")

    retry_adapter_class = RETRY_EXECUTION_MODE_TO_ADAPTER.get(execution_mode)
    if retry_adapter_class is None:
        return _reject("no_retry_adapter_for_execution_mode")

    if retry_adapter_class not in ALLOWED_RETRY_ADAPTERS:
        return _reject("invalid_retry_adapter_class")

    if retry_adapter_class not in ROUTE_TO_ALLOWED_RETRY_ADAPTERS.get(
        failure_retry_decision["route_class"], set()
    ):
        return _reject("retry_adapter_route_mismatch")

    if (
        failure_retry_decision.get("retry_eligible") is not True
        or failure_retry_decision.get("terminal") is True
    ):
        return _denied_retry_result(failure_retry_decision, retry_adapter_class)

    retry_adapter_fn = RETRY_ADAPTER_FUNCTIONS.get(retry_adapter_class)
    if retry_adapter_fn is None:
        return _reject("missing_retry_adapter_function")

    retry_adapter_result = retry_adapter_fn(failure_retry_decision)

    result_payload = {
        "retry_execution_id": f"RTX-{failure_retry_decision['failure_retry_decision_id']}",
        "retry_execution_result_type": "retry_execution_result_v1",
        "timestamp": _utc_timestamp(),
        "summary": retry_adapter_result["summary"],
        "result": retry_adapter_result["result"],
        "failure_retry_decision_ref": failure_retry_decision["failure_retry_decision_id"],
        "delivery_outcome_receipt_ref": failure_retry_decision["delivery_outcome_receipt_ref"],
        "transport_execution_ref": failure_retry_decision["transport_execution_ref"],
        "transport_envelope_ref": failure_retry_decision["transport_envelope_ref"],
        "ack_index_ref": failure_retry_decision["ack_index_ref"],
        "payload_class": failure_retry_decision["payload_class"],
        "route_class": failure_retry_decision["route_class"],
        "execution_mode": failure_retry_decision["execution_mode"],
        "source_adapter_class": source_adapter_class,
        "retry_adapter_class": retry_adapter_class,
        "retry_attempted": retry_adapter_result["retry_attempted"],
        "retry_permitted": True,
        "terminal": failure_retry_decision["terminal"],
        "retry_eligible": failure_retry_decision["retry_eligible"],
        "escalation_suggested": failure_retry_decision["escalation_suggested"],
    }

    result_validation = _validate_required_fields(
        payload=result_payload,
        required_fields=REQUIRED_RETRY_EXECUTION_RESULT_FIELDS,
        prefix="retry_execution_result",
    )
    if result_validation is not None:
        return result_validation

    if (
        result_payload["retry_execution_result_type"]
        not in ALLOWED_RETRY_EXECUTION_RESULT_TYPES
    ):
        return _reject("invalid_retry_execution_result_type")

    return {
        "status": "ok",
        "retry_execution_result": result_payload,
    }