from __future__ import annotations

from typing import Dict, Set, Tuple

REVIEW_STAGE_ID = "stage24_child_core_review"

DISALLOWED_AUTHORITIES: Tuple[str, ...] = (
    "watcher_execution",
    "continuity_mutation",
    "publication",
    "delivery",
    "output_rebuild",
    "runtime_reinvocation",
    "pm_state_mutation",
    "canon_state_mutation",
)

ALLOWED_DOWNSTREAM_TARGETS: Dict[str, Set[str]] = {
    "contractor_proposals_core": {
        "watcher_intake",
        "manual_review_queue",
        "continuity_intake",
    },
    "louisville_gis_core": {
        "watcher_intake",
        "manual_review_queue",
        "continuity_intake",
    },
}

DEFAULT_TARGETS: Dict[str, str] = {
    "contractor_proposals_core": "watcher_intake",
    "louisville_gis_core": "watcher_intake",
}

HOLD_TARGET = "hold"
TERMINATE_TARGET = "terminate"