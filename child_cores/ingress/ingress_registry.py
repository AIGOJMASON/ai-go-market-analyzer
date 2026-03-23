from __future__ import annotations

INGRESS_REGISTRY = {
    "layer": "CHILD_CORE_INGRESS",
    "stage": 21,
    "identity": "Child-core ingress / runtime boundary",
    "accepted_artifacts": [
        "dispatch_packet",
    ],
    "emitted_artifacts": [
        "ingress_receipt",
        "ingress_failure_receipt",
    ],
    "state_surface": [
        "last_ingress_id",
        "last_target_core",
        "last_timestamp",
    ],
    "authority": {
        "allowed": [
            "validate_ingress_eligibility",
            "resolve_declared_ingress_surface",
            "emit_ingress_receipt",
            "handoff_to_declared_ingress_handler",
            "terminate_invalid_propagation",
        ],
        "disallowed": [
            "create_strategy",
            "rewrite_pm_routing",
            "rewrite_pm_dispatch",
            "reinterpret_arbitrator_truth",
            "perform_domain_execution_beyond_handoff",
            "coordinate_multi_core_workflows",
            "mutate_canon",
            "become_runtime_orchestrator",
        ],
    },
}