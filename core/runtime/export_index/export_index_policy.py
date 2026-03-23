from __future__ import annotations

EXPORT_INDEX_FIELD_POLICY = {
    "runtime_export_index": [
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
}

REQUIRED_MANIFEST_FIELDS_FOR_EXPORT_INDEX = [
    "manifest_id",
    "manifest_type",
    "timestamp",
    "summary",
    "result",
    "bundle_ref",
    "bundle_type",
    "report_count",
]