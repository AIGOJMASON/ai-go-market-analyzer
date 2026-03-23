from __future__ import annotations

PM_CONTINUITY_REGISTRY = {
    "layer_id": "PM_CONTINUITY",
    "stage": 17,
    "status": "defined",
    "authority_class": "pm_decision_memory",
    "entrypoint": "AI_GO/PM_CORE/smi/pm_continuity.py:update_pm_continuity",
    "accepted_artifacts": [
        "pm_intake_record",
        "pm_refinement_record",
        "strategic_interpretation_record"
    ],
    "emitted_artifacts": [
        "pm_continuity_update",
        "pm_continuity_receipt"
    ],
    "state_surfaces": [
        "AI_GO/PM_CORE/state/current/pm_continuity_state.json",
        "AI_GO/PM_CORE/state/current/pm_change_ledger.json",
        "AI_GO/PM_CORE/state/current/pm_unresolved_queue.json"
    ],
    "disallowed_authorities": [
        "research_truth_mutation",
        "arbitration_rescoring",
        "child_core_activation",
        "pm_routing_execution",
        "canon_truth_mutation"
    ],
    "notes": "PM_CONTINUITY is a PM-owned memory layer that preserves bounded decision continuity after Stage 16 arbitration."
}