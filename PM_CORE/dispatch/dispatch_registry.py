from __future__ import annotations

DISPATCH_REGISTRY = {
    "layer": "PM_DISPATCH",
    "stage": 20,
    "identity": "PM routing-to-dispatch execution boundary",
    "accepted_artifacts": [
        "pm_routing_packet",
    ],
    "emitted_artifacts": [
        "dispatch_packet",
        "dispatch_failure_receipt",
    ],
    "state_surface": [
        "last_dispatch_id",
        "last_target",
        "last_timestamp",
    ],
    "authority": {
        "allowed": [
            "validate_dispatch_eligibility",
            "resolve_declared_destination_surface",
            "emit_dispatch_artifact",
            "terminate_invalid_propagation",
        ],
        "disallowed": [
            "create_strategy",
            "rewrite_pm_routing",
            "reinterpret_arbitrator_truth",
            "execute_child_core_internal_work",
            "fanout_multi_core_dispatch",
            "mutate_canon",
            "perform_open_orchestration",
        ],
    },
}