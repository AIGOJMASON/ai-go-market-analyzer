from __future__ import annotations

REPORT_BUNDLE_FIELD_POLICY = {
    "runtime_report_bundle": [
        "bundle_id",
        "bundle_type",
        "timestamp",
        "summary",
        "result",
        "report_refs",
        "report_count",
    ]
}

REQUIRED_REPORT_FIELDS_FOR_BUNDLE = [
    "report_id",
    "report_type",
    "timestamp",
    "summary",
    "result",
]