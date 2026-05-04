from __future__ import annotations

OPERATOR_SUMMARY_FIELD_POLICY = {
    "runtime_overview": [
        "summary_id",
        "summary_class",
        "timestamp",
        "summary",
        "result",
    ],
    "stage_overview": [
        "summary_id",
        "summary_class",
        "timestamp",
        "summary",
        "stage",
        "result",
    ],
    "probe_overview": [
        "summary_id",
        "summary_class",
        "timestamp",
        "summary",
        "probe_refs",
        "result",
    ],
    "surface_readiness": [
        "summary_id",
        "summary_class",
        "timestamp",
        "summary",
        "surface_refs",
        "result",
    ],
}

APPROVED_SOURCE_STATUS_CLASSES = {
    "runtime_overview": ["runtime_readiness"],
    "stage_overview": ["stage_completion"],
    "probe_overview": ["probe_health"],
    "surface_readiness": ["output_health", "consumption_health", "runtime_readiness"],
}