from __future__ import annotations

STATUS_FIELD_POLICY = {
    "runtime_readiness": [
        "status_id",
        "status_class",
        "timestamp",
        "summary",
        "result",
    ],
    "stage_completion": [
        "status_id",
        "status_class",
        "timestamp",
        "summary",
        "stage",
        "result",
    ],
    "probe_health": [
        "status_id",
        "status_class",
        "timestamp",
        "summary",
        "probe_ref",
        "result",
    ],
    "output_health": [
        "status_id",
        "status_class",
        "timestamp",
        "summary",
        "stage",
        "probe_ref",
        "result",
    ],
    "consumption_health": [
        "status_id",
        "status_class",
        "timestamp",
        "summary",
        "stage",
        "probe_ref",
        "result",
    ],
}