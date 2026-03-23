from __future__ import annotations

from typing import Any, Dict, List

from .report_bundle_policy import (
    REPORT_BUNDLE_FIELD_POLICY,
    REQUIRED_REPORT_FIELDS_FOR_BUNDLE,
)
from .report_bundle_registry import REPORT_BUNDLE_REGISTRY


REQUIRED_BUNDLE_FIELDS = [
    "bundle_id",
    "bundle_type",
    "timestamp",
    "summary",
    "result",
    "report_refs",
    "report_count",
]


def validate_bundle_type(bundle_type: str) -> Dict[str, Any]:
    if bundle_type not in REPORT_BUNDLE_REGISTRY:
        return {
            "ok": False,
            "reason": "unknown_bundle_type",
            "bundle_type": bundle_type,
        }
    return {"ok": True}


def validate_bundle_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    missing_fields = [field for field in REQUIRED_BUNDLE_FIELDS if field not in payload]
    if missing_fields:
        return {
            "ok": False,
            "reason": "missing_required_fields",
            "missing_fields": missing_fields,
        }

    type_result = validate_bundle_type(payload["bundle_type"])
    if not type_result["ok"]:
        return type_result

    return {"ok": True}


def validate_report_payloads(
    bundle_type: str, report_payloads: List[Dict[str, Any]]
) -> Dict[str, Any]:
    allowed_report_types = REPORT_BUNDLE_REGISTRY[bundle_type]["allowed_report_types"]

    for payload in report_payloads:
        missing_fields = [
            field for field in REQUIRED_REPORT_FIELDS_FOR_BUNDLE if field not in payload
        ]
        if missing_fields:
            return {
                "ok": False,
                "reason": "report_payload_missing_required_fields",
                "missing_fields": missing_fields,
            }

        if payload["report_type"] not in allowed_report_types:
            return {
                "ok": False,
                "reason": "unapproved_report_type",
                "report_type": payload["report_type"],
            }

    return {"ok": True}


def shape_report_bundle(
    payload: Dict[str, Any], report_payloads: List[Dict[str, Any]]
) -> Dict[str, Any]:
    payload_result = validate_bundle_payload(payload)
    if not payload_result["ok"]:
        raise ValueError(f"Invalid bundle payload: {payload_result}")

    reports_result = validate_report_payloads(payload["bundle_type"], report_payloads)
    if not reports_result["ok"]:
        raise ValueError(f"Invalid report payloads for bundle: {reports_result}")

    allowed_fields = REPORT_BUNDLE_FIELD_POLICY[payload["bundle_type"]]
    shaped = {field: payload[field] for field in allowed_fields if field in payload}
    return shaped


def get_report_bundle_view(
    payload: Dict[str, Any], report_payloads: List[Dict[str, Any]]
) -> Dict[str, Any]:
    return shape_report_bundle(payload, report_payloads)