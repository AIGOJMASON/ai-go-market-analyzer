from __future__ import annotations

ACK_INDEX_FIELD_POLICY = {
    "runtime_ack_index": [
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
}

REQUIRED_DELIVERY_RECEIPT_FIELDS_FOR_ACK_INDEX = [
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