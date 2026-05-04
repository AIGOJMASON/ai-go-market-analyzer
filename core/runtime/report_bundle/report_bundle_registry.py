from __future__ import annotations

REPORT_BUNDLE_REGISTRY = {
    "runtime_report_bundle": {
        "type": "read_only_report_bundle",
        "allowed_report_types": [
            "status_report",
            "operator_summary_report",
            "runtime_brief_report",
        ],
    }
}