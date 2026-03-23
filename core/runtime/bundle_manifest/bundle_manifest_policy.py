from __future__ import annotations

BUNDLE_MANIFEST_FIELD_POLICY = {
    "runtime_bundle_manifest": [
        "manifest_id",
        "manifest_type",
        "timestamp",
        "summary",
        "result",
        "bundle_ref",
        "bundle_type",
        "report_count",
    ]
}

REQUIRED_BUNDLE_FIELDS_FOR_MANIFEST = [
    "bundle_id",
    "bundle_type",
    "timestamp",
    "summary",
    "result",
    "report_refs",
    "report_count",
]