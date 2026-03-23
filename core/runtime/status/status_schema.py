from __future__ import annotations

REQUIRED_STATUS_FIELDS = [
    "status_id",
    "status_class",
    "timestamp",
    "summary",
]

OPTIONAL_STATUS_FIELDS = [
    "stage",
    "probe_ref",
    "result",
    "details",
]