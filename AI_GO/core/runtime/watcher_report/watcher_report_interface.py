from __future__ import annotations

from typing import Any, Dict

from .watcher_report_policy import (
    APPROVED_SOURCE_KEYS,
    WATCHER_REPORT_FIELD_POLICY,
)
from .watcher_report_registry import WATCHER_REPORT_REGISTRY


REQUIRED_REPORT_FIELDS = [
    "report_id",
    "report_type",
    "timestamp",
    "summary",
    "result",
]


def validate_report_type(report_type: str) -> Dict[str, Any]:
    if report_type not in WATCHER_REPORT_REGISTRY:
        return {
            "ok": False,
            "reason": "unknown_report_type",
            "report_type": report_type,
        }
    return {"ok": True}


def validate_report_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    missing_fields = [field for field in REQUIRED_REPORT_FIELDS if field not in payload]
    if missing_fields:
        return {
            "ok": False,
            "reason": "missing_required_fields",
            "missing_fields": missing_fields,
        }

    type_result = validate_report_type(payload["report_type"])
    if not type_result["ok"]:
        return type_result

    return {"ok": True}


def validate_source_payload(report_type: str, source_payload: Dict[str, Any]) -> Dict[str, Any]:
    approved_keys = APPROVED_SOURCE_KEYS[report_type]
    missing_keys = [key for key in approved_keys if key not in source_payload]

    if missing_keys:
        return {
            "ok": False,
            "reason": "source_payload_missing_approved_keys",
            "missing_keys": missing_keys,
        }

    return {"ok": True}


def shape_watcher_report(
    payload: Dict[str, Any], source_payload: Dict[str, Any]
) -> Dict[str, Any]:
    payload_result = validate_report_payload(payload)
    if not payload_result["ok"]:
        raise ValueError(f"Invalid report payload: {payload_result}")

    source_result = validate_source_payload(payload["report_type"], source_payload)
    if not source_result["ok"]:
        raise ValueError(f"Invalid report source payload: {source_result}")

    allowed_fields = WATCHER_REPORT_FIELD_POLICY[payload["report_type"]]
    shaped = {field: payload[field] for field in allowed_fields if field in payload}
    return shaped


def get_watcher_report_view(
    payload: Dict[str, Any], source_payload: Dict[str, Any]
) -> Dict[str, Any]:
    return shape_watcher_report(payload, source_payload)