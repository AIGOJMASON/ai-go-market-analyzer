from __future__ import annotations

DELIVERY_RECEIPT_FIELD_POLICY = {
    "runtime_delivery_receipt": [
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
}

REQUIRED_DELIVERY_INDEX_FIELDS_FOR_RECEIPT = [
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