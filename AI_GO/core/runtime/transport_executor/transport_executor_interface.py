from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from .transport_executor_adapters import (
    gated_auto_release_adapter,
    manual_release_adapter,
)
from .transport_executor_policy import (
    INTERNAL_FIELD_NAMES,
    REQUIRED_EXECUTION_RESULT_FIELDS,
    REQUIRED_TRANSPORT_ENVELOPE_FIELDS,
)
from .transport_executor_registry import (
    ALLOWED_EXECUTION_MODES,
    ALLOWED_EXECUTION_RESULT_TYPES,
    ALLOWED_PAYLOAD_CLASSES,
    ALLOWED_ROUTE_CLASSES,
    ALLOWED_TRANSPORT_ENVELOPE_TYPES,
    EXECUTION_MODE_TO_ADAPTER,
    ROUTE_TO_ALLOWED_ADAPTERS,
)


ADAPTER_FUNCTIONS = {
    "manual_release_adapter": manual_release_adapter,
    "gated_auto_release_adapter": gated_auto_release_adapter,
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


def _denied_result(envelope: Dict[str, Any], adapter_class: str) -> Dict[str, Any]:
    result_payload = {
        "transport_execution_id": f"TX-{envelope['transport_envelope_id']}",
        "transport_execution_result_type": "transport_execution_result_v1",
        "timestamp": _utc_timestamp(),
        "summary": "Transport execution denied by permission gate.",
        "result": "denied",
        "transport_envelope_ref": envelope["transport_envelope_id"],
        "transport_envelope_type": envelope["transport_envelope_type"],
        "ack_index_ref": envelope["ack_index_ref"],
        "payload_class": envelope["payload_class"],
        "route_class": envelope["route_class"],
        "execution_mode": envelope["execution_mode"],
        "adapter_class": adapter_class,
        "execution_attempted": False,
        "execution_permitted": False,
    }
    return {
        "status": "ok",
        "transport_execution_result": result_payload,
    }


def execute_transport_envelope(transport_envelope: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(transport_envelope, dict):
        return _reject("invalid_transport_envelope_payload")

    if _contains_internal_fields(transport_envelope):
        return _reject("internal_field_leakage")

    envelope_validation = _validate_required_fields(
        payload=transport_envelope,
        required_fields=REQUIRED_TRANSPORT_ENVELOPE_FIELDS,
        prefix="transport_envelope",
    )
    if envelope_validation is not None:
        return envelope_validation

    if transport_envelope.get("transport_envelope_type") not in ALLOWED_TRANSPORT_ENVELOPE_TYPES:
        return _reject("unapproved_transport_envelope_type")

    if transport_envelope.get("payload_class") not in ALLOWED_PAYLOAD_CLASSES:
        return _reject("invalid_payload_class")

    if transport_envelope.get("route_class") not in ALLOWED_ROUTE_CLASSES:
        return _reject("invalid_route_class")

    execution_mode = transport_envelope.get("execution_mode")
    if execution_mode not in ALLOWED_EXECUTION_MODES:
        return _reject("invalid_execution_mode")

    adapter_class = EXECUTION_MODE_TO_ADAPTER.get(execution_mode)
    if adapter_class is None:
        return _reject("no_adapter_for_execution_mode")

    if adapter_class not in ROUTE_TO_ALLOWED_ADAPTERS.get(transport_envelope["route_class"], set()):
        return _reject("adapter_route_mismatch")

    if transport_envelope.get("transport_permitted") is not True:
        return _denied_result(transport_envelope, adapter_class)

    adapter_fn = ADAPTER_FUNCTIONS.get(adapter_class)
    if adapter_fn is None:
        return _reject("missing_adapter_function")

    adapter_result = adapter_fn(transport_envelope)

    result_payload = {
        "transport_execution_id": f"TX-{transport_envelope['transport_envelope_id']}",
        "transport_execution_result_type": "transport_execution_result_v1",
        "timestamp": _utc_timestamp(),
        "summary": adapter_result["summary"],
        "result": adapter_result["result"],
        "transport_envelope_ref": transport_envelope["transport_envelope_id"],
        "transport_envelope_type": transport_envelope["transport_envelope_type"],
        "ack_index_ref": transport_envelope["ack_index_ref"],
        "payload_class": transport_envelope["payload_class"],
        "route_class": transport_envelope["route_class"],
        "execution_mode": transport_envelope["execution_mode"],
        "adapter_class": adapter_class,
        "execution_attempted": adapter_result["execution_attempted"],
        "execution_permitted": True,
    }

    result_validation = _validate_required_fields(
        payload=result_payload,
        required_fields=REQUIRED_EXECUTION_RESULT_FIELDS,
        prefix="transport_execution_result",
    )
    if result_validation is not None:
        return result_validation

    if result_payload["transport_execution_result_type"] not in ALLOWED_EXECUTION_RESULT_TYPES:
        return _reject("invalid_transport_execution_result_type")

    return {
        "status": "ok",
        "transport_execution_result": result_payload,
    }