from __future__ import annotations

REFINEMENT_REGISTRY = {
    "layer_id": "PM_CORE.REFINEMENT",
    "status": "active",
    "surfaces": {
        "pm_refinement": {
            "entrypoint": "AI_GO/PM_CORE/refinement/pm_refinement.py",
            "authority_class": "pm_refinement",
            "accepted_artifacts": [
                "pm_intake_record",
                "pm_continuity_update"
            ],
            "emitted_artifacts": [
                "pm_refinement_record"
            ],
        },
        "strategic_interpretation": {
            "entrypoint": "AI_GO/PM_CORE/refinement/strategic_interpretation.py",
            "authority_class": "strategic_interpretation",
            "accepted_artifacts": [
                "pm_refinement_record",
                "pm_continuity_update",
                "pm_decision_packet"
            ],
            "emitted_artifacts": [
                "strategic_interpretation_record"
            ],
        },
        "arbitration_intake": {
            "entrypoint": "AI_GO/PM_CORE/refinement/arbitration_intake.py:intake_arbitration_decision",
            "authority_class": "pm_intake",
            "accepted_artifacts": [
                "arbitration_decision_packet"
            ],
            "emitted_artifacts": [
                "pm_intake_record",
                "pm_intake_receipt"
            ],
        },
        "pm_continuity": {
            "entrypoint": "AI_GO/PM_CORE/smi/pm_continuity.py:update_pm_continuity",
            "authority_class": "pm_decision_memory",
            "accepted_artifacts": [
                "pm_intake_record"
            ],
            "emitted_artifacts": [
                "pm_continuity_update",
                "pm_continuity_receipt"
            ],
        },
        "pm_strategy": {
            "entrypoint": "AI_GO/PM_CORE/strategy/pm_strategy.py:run_pm_strategy",
            "authority_class": "pm_decision",
            "accepted_artifacts": [
                "pm_continuity_update"
            ],
            "emitted_artifacts": [
                "pm_decision_packet",
                "pm_strategy_receipt"
            ],
        },
    },
    "notes": "PM refinement registry includes arbitration intake, PM continuity, and PM strategy as separate PM-side surfaces without granting routing or execution authority.",
}