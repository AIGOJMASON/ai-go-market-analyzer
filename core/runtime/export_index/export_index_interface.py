from __future__ import annotations

from typing import Any, Dict

from .export_index_policy import (
    EXPORT_INDEX_FIELD_POLICY,
    REQUIRED_MANIFEST_FIELDS_FOR_EXPORT_INDEX,
)
from .export_index_registry import EXPORT_INDEX_REGISTRY


REQUIRED_EXPORT_INDEX_FIELDS = [
    "export_index_id",
    "export_index_type",
    "timestamp",
    "summary",
    "result",
    "manifest_ref",
    "manifest_type",
    "bundle_ref",
    "report_count",
    "dispatch_ready",
]


def validate_export_index_type(export_index_type: str) -> Dict[str, Any]:
    if export_index_type not in EXPORT_INDEX_REGISTRY:
        return {
            "ok": False,
            "reason": "unknown_export_index_type",
            "export_index_type": export_index_type,
        }
    return {"ok": True}


def validate_export_index_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    missing_fields = [field for field in REQUIRED_EXPORT_INDEX_FIELDS if field not in payload]
    if missing_fields:
        return {
            "ok": False,
            "reason": "missing_required_fields",
            "missing_fields": missing_fields,
        }

    type_result = validate_export_index_type(payload["export_index_type"])
    if not type_result["ok"]:
        return type_result

    allowed_manifest_types = EXPORT_INDEX_REGISTRY[payload["export_index_type"]]["allowed_manifest_types"]
    if payload["manifest_type"] not in allowed_manifest_types:
        return {
            "ok": False,
            "reason": "unapproved_manifest_type",
            "manifest_type": payload["manifest_type"],
        }

    return {"ok": True}


def validate_manifest_payload(manifest_payload: Dict[str, Any]) -> Dict[str, Any]:
    missing_fields = [
        field for field in REQUIRED_MANIFEST_FIELDS_FOR_EXPORT_INDEX if field not in manifest_payload
    ]
    if missing_fields:
        return {
            "ok": False,
            "reason": "manifest_payload_missing_required_fields",
            "missing_fields": missing_fields,
        }

    return {"ok": True}


def shape_export_index(
    payload: Dict[str, Any], manifest_payload: Dict[str, Any]
) -> Dict[str, Any]:
    payload_result = validate_export_index_payload(payload)
    if not payload_result["ok"]:
        raise ValueError(f"Invalid export index payload: {payload_result}")

    manifest_result = validate_manifest_payload(manifest_payload)
    if not manifest_result["ok"]:
        raise ValueError(f"Invalid manifest payload for export index: {manifest_result}")

    allowed_fields = EXPORT_INDEX_FIELD_POLICY[payload["export_index_type"]]
    shaped = {field: payload[field] for field in allowed_fields if field in payload}
    return shaped


def get_export_index_view(
    payload: Dict[str, Any], manifest_payload: Dict[str, Any]
) -> Dict[str, Any]:
    return shape_export_index(payload, manifest_payload)