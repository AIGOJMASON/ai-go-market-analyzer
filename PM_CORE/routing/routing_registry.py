from __future__ import annotations

ROUTING_REGISTRY = {
    "layer": "PM_ROUTING",
    "stage": 19,
    "identity": "PM decision-to-routing handoff",
    "accepted_artifacts": [
        "pm_decision_packet",
    ],
    "emitted_artifacts": [
        "pm_routing_packet",
        "pm_routing_failure_receipt",
    ],
    "state_surface": [
        "last_packet_id",
        "last_timestamp",
        "last_target_set",
    ],
    "authority": {
        "allowed": [
            "validate",
            "normalize",
            "compress",
            "terminate_invalid_propagation",
        ],
        "disallowed": [
            "create_strategy",
            "rewrite_pm_continuity",
            "rescore_research",
            "reinterpret_arbitrator_truth",
            "execute_routing",
            "activate_child_core",
            "mutate_canon",
        ],
    },
}