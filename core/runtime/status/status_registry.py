from __future__ import annotations

STATUS_REGISTRY = {
    "runtime_readiness": {
        "type": "read_only_status",
        "description": "bounded runtime readiness summary",
    },
    "stage_completion": {
        "type": "read_only_status",
        "description": "closed stage completion summary",
    },
    "probe_health": {
        "type": "read_only_status",
        "description": "probe pass-fail summary",
    },
    "output_health": {
        "type": "read_only_status",
        "description": "Stage 30 output boundary health summary",
    },
    "consumption_health": {
        "type": "read_only_status",
        "description": "Stage 31 consumption control health summary",
    },
}