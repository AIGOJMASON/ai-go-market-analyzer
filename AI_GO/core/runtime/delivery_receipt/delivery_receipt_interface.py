from __future__ import annotations

from typing import Any, Dict

from .delivery_receipt_policy import (
    DELIVERY_RECEIPT_FIELD_POLICY,
    REQUIRED_DELIVERY_INDEX_FIELDS_FOR_RECEIPT,
)
from .delivery_receipt_registry import DELIVERY_RECEIPT_REGISTRY


REQUIRED_DELIVERY_RECEIPT_FIELDS = [
    "delivery_receipt_id",
    "delivery_receipt_type",
    "timestamp",
    "summary",
    "result",
    "delivery_index_ref",
    "delivery_index_type",
    "dispatch_manifest_ref",
    "manifest_ref",
    "bundle_ref",
    "report_count",
    "accepted",
]


def validate_delivery_receipt_type(delivery_receipt_type: str) -> Dict[str, Any]:
    if delivery_receipt_type not in DELIVERY_RECEIPT_REGISTRY:
        return {
            "ok": False,
            "reason": "unknown_delivery_receipt_type",
            "delivery_receipt_type": delivery_receipt_type,
        }
    return {"ok": True}


def validate_delivery_receipt_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    missing_fields = [
        field for field in REQUIRED_DELIVERY_RECEIPT_FIELDS if field not in payload
    ]
    if missing_fields:
        return {
            "ok": False,
            "reason": "missing_required_fields",
            "missing_fields": missing_fields,
        }

    type_result = validate_delivery_receipt_type(payload["delivery_receipt_type"])
    if not type_result["ok"]:
        return type_result

    allowed_delivery_index_types = DELIVERY_RECEIPT_REGISTRY[
        payload["delivery_receipt_type"]
    ]["allowed_delivery_index_types"]

    if payload["delivery_index_type"] not in allowed_delivery_index_types:
        return {
            "ok": False,
            "reason": "unapproved_delivery_index_type",
            "delivery_index_type": payload["delivery_index_type"],
        }

    return {"ok": True}


def validate_delivery_index_payload(delivery_index_payload: Dict[str, Any]) -> Dict[str, Any]:
    missing_fields = [
        field
        for field in REQUIRED_DELIVERY_INDEX_FIELDS_FOR_RECEIPT
        if field not in delivery_index_payload
    ]
    if missing_fields:
        return {
            "ok": False,
            "reason": "delivery_index_payload_missing_required_fields",
            "missing_fields": missing_fields,
        }

    return {"ok": True}


def shape_delivery_receipt(
    payload: Dict[str, Any], delivery_index_payload: Dict[str, Any]
) -> Dict[str, Any]:
    payload_result = validate_delivery_receipt_payload(payload)
    if not payload_result["ok"]:
        raise ValueError(f"Invalid delivery receipt payload: {payload_result}")

    delivery_index_result = validate_delivery_index_payload(delivery_index_payload)
    if not delivery_index_result["ok"]:
        raise ValueError(
            f"Invalid delivery index payload for receipt: {delivery_index_result}"
        )

    allowed_fields = DELIVERY_RECEIPT_FIELD_POLICY[payload["delivery_receipt_type"]]
    shaped = {field: payload[field] for field in allowed_fields if field in payload}
    return shaped


def get_delivery_receipt_view(
    payload: Dict[str, Any], delivery_index_payload: Dict[str, Any]
) -> Dict[str, Any]:
    return shape_delivery_receipt(payload, delivery_index_payload)