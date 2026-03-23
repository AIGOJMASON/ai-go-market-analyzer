from __future__ import annotations

WATCHER_REPORT_REGISTRY = {
    "status_report": {
        "type": "read_only_watcher_report",
        "source": "stage32_status",
    },
    "operator_summary_report": {
        "type": "read_only_watcher_report",
        "source": "stage33_operator_summary",
    },
    "runtime_brief_report": {
        "type": "read_only_watcher_report",
        "source": "stage34_cli_safe_views",
    },
}