from __future__ import annotations

from typing import Any, Dict

from .ack_index_policy import (
    ACK_INDEX_FIELD_POLICY,
    REQUIRED_DELIVERY_RECEIPT_FIELDS_FOR_ACK_INDEX,
)
from .ack_index_registry import ACK_INDEX_REGISTRY


REQUIRED_ACK_INDEX_FIELDS = [
    "ack_index_id",
    "ack_index_type",
    "timestamp",
    "summary",
    "result",
    "delivery_receipt_ref",
    "delivery_receipt_type",
    "delivery_index_ref",
    "dispatch_manifest_ref",
    "manifest_ref",
    "bundle_ref",
    "report_count",
    "acceptance_registered",
]


def validate_ack_index_type(ack_index_type: str) -> Dict[str, Any]:
    if ack_index_type not in ACK_INDEX_REGISTRY:
        return {
            "ok": False,
            "reason": "unknown_ack_index_type",
            "ack_index_type": ack_index_type,
        }
    return {"ok": True}


def validate_ack_index_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    missing_fields = [field for field in REQUIRED_ACK_INDEX_FIELDS if field not in payload]
    if missing_fields:
        return {
            "ok": False,
            "reason": "missing_required_fields",
            "missing_fields": missing_fields,
        }

    type_result = validate_ack_index_type(payload["ack_index_type"])
    if not type_result["ok"]:
        return type_result

    allowed_delivery_receipt_types = ACK_INDEX_REGISTRY[
        payload["ack_index_type"]
    ]["allowed_delivery_receipt_types"]

    if payload["delivery_receipt_type"] not in allowed_delivery_receipt_types:
        return {
            "ok": False,
            "reason": "unapproved_delivery_receipt_type",
            "delivery_receipt_type": payload["delivery_receipt_type"],
        }

    return {"ok": True}


def validate_delivery_receipt_payload(delivery_receipt_payload: Dict[str, Any]) -> Dict[str, Any]:
    missing_fields = [
        field
        for field in REQUIRED_DELIVERY_RECEIPT_FIELDS_FOR_ACK_INDEX
        if field not in delivery_receipt_payload
    ]
    if missing_fields:
        return {
            "ok": False,
            "reason": "delivery_receipt_payload_missing_required_fields",
            "missing_fields": missing_fields,
        }

    return {"ok": True}


def shape_ack_index(
    payload: Dict[str, Any], delivery_receipt_payload: Dict[str, Any]
) -> Dict[str, Any]:
    payload_result = validate_ack_index_payload(payload)
    if not payload_result["ok"]:
        raise ValueError(f"Invalid ack index payload: {payload_result}")

    delivery_receipt_result = validate_delivery_receipt_payload(delivery_receipt_payload)
    if not delivery_receipt_result["ok"]:
        raise ValueError(
            f"Invalid delivery receipt payload for ack index: {delivery_receipt_result}"
        )

    allowed_fields = ACK_INDEX_FIELD_POLICY[payload["ack_index_type"]]
    shaped = {field: payload[field] for field in allowed_fields if field in payload}
    return shaped


def get_ack_index_view(
    payload: Dict[str, Any], delivery_receipt_payload: Dict[str, Any]
) -> Dict[str, Any]:
    return shape_ack_index(payload, delivery_receipt_payload)