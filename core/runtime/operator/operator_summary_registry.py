from __future__ import annotations

OPERATOR_SUMMARY_REGISTRY = {
    "runtime_overview": {
        "type": "read_only_operator_summary",
        "description": "bounded summary of overall runtime condition",
    },
    "stage_overview": {
        "type": "read_only_operator_summary",
        "description": "bounded summary of current stage completion state",
    },
    "probe_overview": {
        "type": "read_only_operator_summary",
        "description": "bounded summary of recent governed probe outcomes",
    },
    "surface_readiness": {
        "type": "read_only_operator_summary",
        "description": "bounded summary of readiness across runtime surfaces",
    },
}