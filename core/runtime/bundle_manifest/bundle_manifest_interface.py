from __future__ import annotations

from typing import Any, Dict

from .bundle_manifest_policy import (
    BUNDLE_MANIFEST_FIELD_POLICY,
    REQUIRED_BUNDLE_FIELDS_FOR_MANIFEST,
)
from .bundle_manifest_registry import BUNDLE_MANIFEST_REGISTRY


REQUIRED_MANIFEST_FIELDS = [
    "manifest_id",
    "manifest_type",
    "timestamp",
    "summary",
    "result",
    "bundle_ref",
    "bundle_type",
    "report_count",
]


def validate_manifest_type(manifest_type: str) -> Dict[str, Any]:
    if manifest_type not in BUNDLE_MANIFEST_REGISTRY:
        return {
            "ok": False,
            "reason": "unknown_manifest_type",
            "manifest_type": manifest_type,
        }
    return {"ok": True}


def validate_manifest_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    missing_fields = [field for field in REQUIRED_MANIFEST_FIELDS if field not in payload]
    if missing_fields:
        return {
            "ok": False,
            "reason": "missing_required_fields",
            "missing_fields": missing_fields,
        }

    type_result = validate_manifest_type(payload["manifest_type"])
    if not type_result["ok"]:
        return type_result

    allowed_bundle_types = BUNDLE_MANIFEST_REGISTRY[payload["manifest_type"]]["allowed_bundle_types"]
    if payload["bundle_type"] not in allowed_bundle_types:
        return {
            "ok": False,
            "reason": "unapproved_bundle_type",
            "bundle_type": payload["bundle_type"],
        }

    return {"ok": True}


def validate_bundle_payload(bundle_payload: Dict[str, Any]) -> Dict[str, Any]:
    missing_fields = [
        field for field in REQUIRED_BUNDLE_FIELDS_FOR_MANIFEST if field not in bundle_payload
    ]
    if missing_fields:
        return {
            "ok": False,
            "reason": "bundle_payload_missing_required_fields",
            "missing_fields": missing_fields,
        }

    return {"ok": True}


def shape_bundle_manifest(
    payload: Dict[str, Any], bundle_payload: Dict[str, Any]
) -> Dict[str, Any]:
    payload_result = validate_manifest_payload(payload)
    if not payload_result["ok"]:
        raise ValueError(f"Invalid manifest payload: {payload_result}")

    bundle_result = validate_bundle_payload(bundle_payload)
    if not bundle_result["ok"]:
        raise ValueError(f"Invalid bundle payload for manifest: {bundle_result}")

    allowed_fields = BUNDLE_MANIFEST_FIELD_POLICY[payload["manifest_type"]]
    shaped = {field: payload[field] for field in allowed_fields if field in payload}
    return shaped


def get_bundle_manifest_view(
    payload: Dict[str, Any], bundle_payload: Dict[str, Any]
) -> Dict[str, Any]:
    return shape_bundle_manifest(payload, bundle_payload)