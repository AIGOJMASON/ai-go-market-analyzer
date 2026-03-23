from __future__ import annotations

DISPATCH_MANIFEST_FIELD_POLICY = {
    "runtime_dispatch_manifest": [
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
}

REQUIRED_EXPORT_INDEX_FIELDS_FOR_DISPATCH = [
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