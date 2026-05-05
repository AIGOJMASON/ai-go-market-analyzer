from __future__ import annotations

WATCHER_REPORT_FIELD_POLICY = {
    "status_report": [
        "report_id",
        "report_type",
        "timestamp",
        "summary",
        "result",
    ],
    "operator_summary_report": [
        "report_id",
        "report_type",
        "timestamp",
        "summary",
        "result",
    ],
    "runtime_brief_report": [
        "report_id",
        "report_type",
        "timestamp",
        "summary",
        "result",
        "rendered_block",
    ],
}

APPROVED_SOURCE_KEYS = {
    "status_report": [
        "status_id",
        "status_class",
        "timestamp",
        "summary",
        "result",
    ],
    "operator_summary_report": [
        "summary_id",
        "summary_class",
        "timestamp",
        "summary",
        "result",
    ],
    "runtime_brief_report": [
        "rendered_block",
        "summary",
        "timestamp",
    ],
}