from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from .escalation_executor_adapters import (
    operator_queue_escalation_adapter,
    retry_governance_escalation_adapter,
)
from .escalation_executor_policy import (
    INTERNAL_FIELD_NAMES,
    REQUIRED_ESCALATION_DECISION_FIELDS,
    REQUIRED_ESCALATION_EXECUTION_RESULT_FIELDS,
)
from .escalation_executor_registry import (
    ALLOWED_ESCALATION_ADAPTERS,
    ALLOWED_ESCALATION_CLASSES,
    ALLOWED_ESCALATION_DECISION_TYPES,
    ALLOWED_ESCALATION_EXECUTION_RESULT_TYPES,
    ALLOWED_ESCALATION_ROUTES,
    ALLOWED_EXECUTION_MODES,
    ALLOWED_PAYLOAD_CLASSES,
    ALLOWED_RETRY_ADAPTER_CLASSES,
    ALLOWED_ROUTE_CLASSES,
    ALLOWED_SOURCE_ADAPTER_CLASSES,
    ESCALATION_ROUTE_TO_ADAPTER,
)


ESCALATION_ADAPTER_FUNCTIONS = {
    "operator_queue_escalation_adapter": operator_queue_escalation_adapter,
    "retry_governance_escalation_adapter": retry_governance_escalation_adapter,
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


def _denied_escalation_result(
    decision: Dict[str, Any],
    escalation_adapter_class: str,
) -> Dict[str, Any]:
    result_payload = {
        "escalation_execution_id": f"EEX-{decision['escalation_decision_id']}",
        "escalation_execution_result_type": "escalation_execution_result_v1",
        "timestamp": _utc_timestamp(),
        "summary": "Escalation execution denied by escalation decision gate.",
        "result": "escalation_denied",
        "escalation_decision_ref": decision["escalation_decision_id"],
        "source_receipt_ref": decision["source_receipt_ref"],
        "source_receipt_type": decision["source_receipt_type"],
        "payload_class": decision["payload_class"],
        "route_class": decision["route_class"],
        "execution_mode": decision["execution_mode"],
        "source_adapter_class": decision["source_adapter_class"],
        "retry_adapter_class": decision["retry_adapter_class"],
        "escalation_class": decision["escalation_class"],
        "escalation_route": decision["escalation_route"],
        "escalation_adapter_class": escalation_adapter_class,
        "escalation_attempted": False,
        "escalation_permitted": False,
    }
    return {
        "status": "ok",
        "escalation_execution_result": result_payload,
    }


def execute_escalation_decision(escalation_decision: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(escalation_decision, dict):
        return _reject("invalid_escalation_decision_payload")

    if _contains_internal_fields(escalation_decision):
        return _reject("internal_field_leakage")

    validation = _validate_required_fields(
        payload=escalation_decision,
        required_fields=REQUIRED_ESCALATION_DECISION_FIELDS,
        prefix="escalation_decision",
    )
    if validation is not None:
        return validation

    if (
        escalation_decision.get("escalation_decision_type")
        not in ALLOWED_ESCALATION_DECISION_TYPES
    ):
        return _reject("unapproved_escalation_decision_type")

    if escalation_decision.get("payload_class") not in ALLOWED_PAYLOAD_CLASSES:
        return _reject("invalid_payload_class")

    if escalation_decision.get("route_class") not in ALLOWED_ROUTE_CLASSES:
        return _reject("invalid_route_class")

    if escalation_decision.get("execution_mode") not in ALLOWED_EXECUTION_MODES:
        return _reject("invalid_execution_mode")

    if (
        escalation_decision.get("source_adapter_class")
        not in ALLOWED_SOURCE_ADAPTER_CLASSES
    ):
        return _reject("invalid_source_adapter_class")

    if (
        escalation_decision.get("retry_adapter_class")
        not in ALLOWED_RETRY_ADAPTER_CLASSES
    ):
        return _reject("invalid_retry_adapter_class")

    if escalation_decision.get("escalation_class") not in ALLOWED_ESCALATION_CLASSES:
        return _reject("invalid_escalation_class")

    if escalation_decision.get("escalation_route") not in ALLOWED_ESCALATION_ROUTES:
        return _reject("invalid_escalation_route")

    escalation_adapter_class = ESCALATION_ROUTE_TO_ADAPTER.get(
        escalation_decision["escalation_route"]
    )
    if escalation_adapter_class not in ALLOWED_ESCALATION_ADAPTERS:
        return _reject("invalid_escalation_adapter_class")

    if escalation_decision.get("escalation_required") is not True:
        return _denied_escalation_result(escalation_decision, escalation_adapter_class)

    if escalation_adapter_class == "none":
        return _reject("no_escalation_adapter_for_required_decision")

    escalation_adapter_fn = ESCALATION_ADAPTER_FUNCTIONS.get(escalation_adapter_class)
    if escalation_adapter_fn is None:
        return _reject("missing_escalation_adapter_function")

    adapter_result = escalation_adapter_fn(escalation_decision)

    result_payload = {
        "escalation_execution_id": f"EEX-{escalation_decision['escalation_decision_id']}",
        "escalation_execution_result_type": "escalation_execution_result_v1",
        "timestamp": _utc_timestamp(),
        "summary": adapter_result["summary"],
        "result": adapter_result["result"],
        "escalation_decision_ref": escalation_decision["escalation_decision_id"],
        "source_receipt_ref": escalation_decision["source_receipt_ref"],
        "source_receipt_type": escalation_decision["source_receipt_type"],
        "payload_class": escalation_decision["payload_class"],
        "route_class": escalation_decision["route_class"],
        "execution_mode": escalation_decision["execution_mode"],
        "source_adapter_class": escalation_decision["source_adapter_class"],
        "retry_adapter_class": escalation_decision["retry_adapter_class"],
        "escalation_class": escalation_decision["escalation_class"],
        "escalation_route": escalation_decision["escalation_route"],
        "escalation_adapter_class": escalation_adapter_class,
        "escalation_attempted": adapter_result["escalation_attempted"],
        "escalation_permitted": True,
    }

    validation = _validate_required_fields(
        payload=result_payload,
        required_fields=REQUIRED_ESCALATION_EXECUTION_RESULT_FIELDS,
        prefix="escalation_execution_result",
    )
    if validation is not None:
        return validation

    if (
        result_payload["escalation_execution_result_type"]
        not in ALLOWED_ESCALATION_EXECUTION_RESULT_TYPES
    ):
        return _reject("invalid_escalation_execution_result_type")

    return {
        "status": "ok",
        "escalation_execution_result": result_payload,
    }