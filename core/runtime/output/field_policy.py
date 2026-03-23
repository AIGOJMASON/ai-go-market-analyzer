from __future__ import annotations

FIELD_POLICY = {
    "watcher": [
        "artifact_id",
        "artifact_type",
        "originating_core",
        "timestamp",
        "summary",
    ],
    "cli": [
        "artifact_id",
        "artifact_type",
        "originating_core",
        "validation_receipt_ref",
        "timestamp",
        "summary",
    ],
    "audit_surface": [
        "artifact_id",
        "artifact_type",
        "originating_core",
        "validation_receipt_ref",
        "lifecycle_state",
        "timestamp",
        "summary",
    ],
}