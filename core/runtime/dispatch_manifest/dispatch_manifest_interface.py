from __future__ import annotations

from typing import Any, Dict

from .dispatch_manifest_policy import (
    DISPATCH_MANIFEST_FIELD_POLICY,
    REQUIRED_EXPORT_INDEX_FIELDS_FOR_DISPATCH,
)
from .dispatch_manifest_registry import DISPATCH_MANIFEST_REGISTRY


REQUIRED_DISPATCH_MANIFEST_FIELDS = [
    "dispatch_manifest_id",
    "dispatch_manifest_type",
    "timestamp",
    "summary",
    "result",
    "export_index_ref",
    "export_index_type",
    "manifest_ref",
    "bundle_ref",
    "report_count",
    "delivery_ready",
]


def validate_dispatch_manifest_type(dispatch_manifest_type: str) -> Dict[str, Any]:
    if dispatch_manifest_type not in DISPATCH_MANIFEST_REGISTRY:
        return {
            "ok": False,
            "reason": "unknown_dispatch_manifest_type",
            "dispatch_manifest_type": dispatch_manifest_type,
        }
    return {"ok": True}


def validate_dispatch_manifest_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    missing_fields = [
        field for field in REQUIRED_DISPATCH_MANIFEST_FIELDS if field not in payload
    ]
    if missing_fields:
        return {
            "ok": False,
            "reason": "missing_required_fields",
            "missing_fields": missing_fields,
        }

    type_result = validate_dispatch_manifest_type(payload["dispatch_manifest_type"])
    if not type_result["ok"]:
        return type_result

    allowed_export_index_types = DISPATCH_MANIFEST_REGISTRY[
        payload["dispatch_manifest_type"]
    ]["allowed_export_index_types"]

    if payload["export_index_type"] not in allowed_export_index_types:
        return {
            "ok": False,
            "reason": "unapproved_export_index_type",
            "export_index_type": payload["export_index_type"],
        }

    return {"ok": True}


def validate_export_index_payload(export_index_payload: Dict[str, Any]) -> Dict[str, Any]:
    missing_fields = [
        field
        for field in REQUIRED_EXPORT_INDEX_FIELDS_FOR_DISPATCH
        if field not in export_index_payload
    ]
    if missing_fields:
        return {
            "ok": False,
            "reason": "export_index_payload_missing_required_fields",
            "missing_fields": missing_fields,
        }

    return {"ok": True}


def shape_dispatch_manifest(
    payload: Dict[str, Any], export_index_payload: Dict[str, Any]
) -> Dict[str, Any]:
    payload_result = validate_dispatch_manifest_payload(payload)
    if not payload_result["ok"]:
        raise ValueError(f"Invalid dispatch manifest payload: {payload_result}")

    export_result = validate_export_index_payload(export_index_payload)
    if not export_result["ok"]:
        raise ValueError(
            f"Invalid export index payload for dispatch manifest: {export_result}"
        )

    allowed_fields = DISPATCH_MANIFEST_FIELD_POLICY[payload["dispatch_manifest_type"]]
    shaped = {field: payload[field] for field in allowed_fields if field in payload}
    return shaped


def get_dispatch_manifest_view(
    payload: Dict[str, Any], export_index_payload: Dict[str, Any]
) -> Dict[str, Any]:
    return shape_dispatch_manifest(payload, export_index_payload)