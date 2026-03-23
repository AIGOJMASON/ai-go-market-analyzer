from __future__ import annotations

from typing import Any, Dict, List

from .operator_summary_policy import (
    APPROVED_SOURCE_STATUS_CLASSES,
    OPERATOR_SUMMARY_FIELD_POLICY,
)
from .operator_summary_registry import OPERATOR_SUMMARY_REGISTRY


REQUIRED_SUMMARY_FIELDS = [
    "summary_id",
    "summary_class",
    "timestamp",
    "summary",
    "result",
]


def validate_summary_class(summary_class: str) -> Dict[str, Any]:
    if summary_class not in OPERATOR_SUMMARY_REGISTRY:
        return {
            "ok": False,
            "reason": "unknown_summary_class",
            "summary_class": summary_class,
        }
    return {"ok": True}


def validate_operator_summary_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    missing_fields = [field for field in REQUIRED_SUMMARY_FIELDS if field not in payload]
    if missing_fields:
        return {
            "ok": False,
            "reason": "missing_required_fields",
            "missing_fields": missing_fields,
        }

    class_result = validate_summary_class(payload["summary_class"])
    if not class_result["ok"]:
        return class_result

    return {"ok": True}


def validate_source_payloads(
    summary_class: str, source_payloads: List[Dict[str, Any]]
) -> Dict[str, Any]:
    approved_classes = APPROVED_SOURCE_STATUS_CLASSES[summary_class]

    for payload in source_payloads:
        status_class = payload.get("status_class")
        if status_class not in approved_classes:
            return {
                "ok": False,
                "reason": "unapproved_source_status_class",
                "summary_class": summary_class,
                "status_class": status_class,
            }

    return {"ok": True}


def shape_operator_summary(
    payload: Dict[str, Any], source_payloads: List[Dict[str, Any]]
) -> Dict[str, Any]:
    payload_result = validate_operator_summary_payload(payload)
    if not payload_result["ok"]:
        raise ValueError(f"Invalid operator summary payload: {payload_result}")

    source_result = validate_source_payloads(payload["summary_class"], source_payloads)
    if not source_result["ok"]:
        raise ValueError(f"Invalid source payloads: {source_result}")

    allowed_fields = OPERATOR_SUMMARY_FIELD_POLICY[payload["summary_class"]]
    shaped = {field: payload[field] for field in allowed_fields if field in payload}
    return shaped


def get_operator_summary_view(
    payload: Dict[str, Any], source_payloads: List[Dict[str, Any]]
) -> Dict[str, Any]:
    return shape_operator_summary(payload, source_payloads)