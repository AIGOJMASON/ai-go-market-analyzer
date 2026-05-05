from __future__ import annotations

from typing import Dict, Tuple

WATCHER_STAGE_ID = "stage25_child_core_watcher"

DISALLOWED_AUTHORITIES: Tuple[str, ...] = (
    "continuity_mutation",
    "publication",
    "delivery",
    "output_rebuild",
    "review_reinvocation",
    "runtime_reinvocation",
    "pm_state_mutation",
    "canon_state_mutation",
)

DECLARED_WATCHER_TARGET = "watcher_intake"


def default_watcher_handler(
    disposition_receipt: dict,
    watcher_context: dict,
) -> dict:
    """
    Default bounded watcher handler.

    Produces compact watcher findings from routed review facts and optional
    bounded watcher flags only.
    """
    findings = {
        "target_core": disposition_receipt["target_core"],
        "source_review_id": disposition_receipt["review_id"],
        "selected_target": disposition_receipt["selected_target"],
        "watcher_flags": watcher_context.get("watcher_flags", []),
        "observation": "watcher_intake_completed",
    }

    input_refs = watcher_context.get("input_refs")
    if input_refs is not None:
        findings["input_refs"] = input_refs

    return {"findings": findings}


WATCHER_HANDLERS: Dict[str, object] = {
    "contractor_proposals_core": default_watcher_handler,
    "louisville_gis_core": default_watcher_handler,
}