from __future__ import annotations

CLI_RENDER_POLICY = {
    "status_view": [
        "status_id",
        "status_class",
        "timestamp",
        "summary",
        "stage",
        "probe_ref",
        "result",
    ],
    "operator_summary_view": [
        "summary_id",
        "summary_class",
        "timestamp",
        "summary",
        "stage",
        "probe_refs",
        "surface_refs",
        "result",
    ],
}