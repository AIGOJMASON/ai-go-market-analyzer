from __future__ import annotations

from typing import Any, Dict

from .status_policy import STATUS_FIELD_POLICY
from .status_registry import STATUS_REGISTRY
from .status_schema import REQUIRED_STATUS_FIELDS


def validate_status_class(status_class: str) -> Dict[str, Any]:
    if status_class not in STATUS_REGISTRY:
        return {
            "ok": False,
            "reason": "unknown_status_class",
            "status_class": status_class,
        }
    return {"ok": True}


def validate_status_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    missing_fields = [field for field in REQUIRED_STATUS_FIELDS if field not in payload]
    if missing_fields:
        return {
            "ok": False,
            "reason": "missing_required_fields",
            "missing_fields": missing_fields,
        }

    class_result = validate_status_class(payload["status_class"])
    if not class_result["ok"]:
        return class_result

    return {"ok": True}


def shape_status_view(payload: Dict[str, Any]) -> Dict[str, Any]:
    validation_result = validate_status_payload(payload)
    if not validation_result["ok"]:
        raise ValueError(f"Invalid status payload: {validation_result}")

    allowed_fields = STATUS_FIELD_POLICY[payload["status_class"]]
    shaped = {field: payload[field] for field in allowed_fields if field in payload}
    return shaped


def get_status_view(payload: Dict[str, Any]) -> Dict[str, Any]:
    return shape_status_view(payload)