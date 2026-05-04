from __future__ import annotations

REGISTRY = {
    "layer_id": "REFINEMENT_ARBITRATOR",
    "stage": 16,
    "status": "active_stub",
    "authority_class": "refinement_governance",
    "entrypoint": "engine.py:run_arbitration",
    "support_modules": [
        "policies.py",
        "profiles.py",
        "receipt.py",
    ],
    "allowed_decisions": [
        "discard",
        "hold",
        "condition_for_child_core",
        "send_to_curved_mirror",
        "send_to_rosetta",
        "pass_to_pm",
    ],
    "disallowed_authorities": [
        "research_truth_mutation",
        "pm_routing_execution",
        "child_core_activation",
        "pm_continuity_memory_authority",
        "registry_truth_mutation",
    ],
}