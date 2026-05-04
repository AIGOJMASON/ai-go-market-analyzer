from __future__ import annotations

from typing import Any, Dict

from .delivery_index_policy import (
    DELIVERY_INDEX_FIELD_POLICY,
    REQUIRED_DISPATCH_MANIFEST_FIELDS_FOR_DELIVERY_INDEX,
)
from .delivery_index_registry import DELIVERY_INDEX_REGISTRY


REQUIRED_DELIVERY_INDEX_FIELDS = [
    "delivery_index_id",
    "delivery_index_type",
    "timestamp",
    "summary",
    "result",
    "dispatch_manifest_ref",
    "dispatch_manifest_type",
    "export_index_ref",
    "manifest_ref",
    "bundle_ref",
    "report_count",
    "registry_complete",
]


def validate_delivery_index_type(delivery_index_type: str) -> Dict[str, Any]:
    if delivery_index_type not in DELIVERY_INDEX_REGISTRY:
        return {
            "ok": False,
            "reason": "unknown_delivery_index_type",
            "delivery_index_type": delivery_index_type,
        }
    return {"ok": True}


def validate_delivery_index_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    missing_fields = [field for field in REQUIRED_DELIVERY_INDEX_FIELDS if field not in payload]
    if missing_fields:
        return {
            "ok": False,
            "reason": "missing_required_fields",
            "missing_fields": missing_fields,
        }

    type_result = validate_delivery_index_type(payload["delivery_index_type"])
    if not type_result["ok"]:
        return type_result

    allowed_dispatch_manifest_types = DELIVERY_INDEX_REGISTRY[
        payload["delivery_index_type"]
    ]["allowed_dispatch_manifest_types"]

    if payload["dispatch_manifest_type"] not in allowed_dispatch_manifest_types:
        return {
            "ok": False,
            "reason": "unapproved_dispatch_manifest_type",
            "dispatch_manifest_type": payload["dispatch_manifest_type"],
        }

    return {"ok": True}


def validate_dispatch_manifest_payload(dispatch_manifest_payload: Dict[str, Any]) -> Dict[str, Any]:
    missing_fields = [
        field
        for field in REQUIRED_DISPATCH_MANIFEST_FIELDS_FOR_DELIVERY_INDEX
        if field not in dispatch_manifest_payload
    ]
    if missing_fields:
        return {
            "ok": False,
            "reason": "dispatch_manifest_payload_missing_required_fields",
            "missing_fields": missing_fields,
        }

    return {"ok": True}


def shape_delivery_index(
    payload: Dict[str, Any], dispatch_manifest_payload: Dict[str, Any]
) -> Dict[str, Any]:
    payload_result = validate_delivery_index_payload(payload)
    if not payload_result["ok"]:
        raise ValueError(f"Invalid delivery index payload: {payload_result}")

    dispatch_result = validate_dispatch_manifest_payload(dispatch_manifest_payload)
    if not dispatch_result["ok"]:
        raise ValueError(
            f"Invalid dispatch manifest payload for delivery index: {dispatch_result}"
        )

    allowed_fields = DELIVERY_INDEX_FIELD_POLICY[payload["delivery_index_type"]]
    shaped = {field: payload[field] for field in allowed_fields if field in payload}
    return shaped


def get_delivery_index_view(
    payload: Dict[str, Any], dispatch_manifest_payload: Dict[str, Any]
) -> Dict[str, Any]:
    return shape_delivery_index(payload, dispatch_manifest_payload)