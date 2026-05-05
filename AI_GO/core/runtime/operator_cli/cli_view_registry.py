from __future__ import annotations

CLI_VIEW_REGISTRY = {
    "status_view": {
        "type": "read_only_cli_view",
        "source": "stage32_status",
    },
    "operator_summary_view": {
        "type": "read_only_cli_view",
        "source": "stage33_operator_summary",
    },
}