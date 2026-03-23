from __future__ import annotations

DELIVERY_INDEX_FIELD_POLICY = {
    "runtime_delivery_index": [
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
}

REQUIRED_DISPATCH_MANIFEST_FIELDS_FOR_DELIVERY_INDEX = [
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