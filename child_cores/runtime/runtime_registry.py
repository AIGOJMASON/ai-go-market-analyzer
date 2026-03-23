from __future__ import annotations

RUNTIME_REGISTRY = {
    "layer": "CHILD_CORE_RUNTIME",
    "stage": 22,
    "identity": "Child-core internal runtime execution boundary",
    "accepted_artifacts": [
        "ingress_receipt",
    ],
    "accepted_companion_context": [
        "runtime_context",
    ],
    "emitted_artifacts": [
        "runtime_receipt",
        "runtime_failure_receipt",
    ],
    "state_surface": [
        "last_runtime_id",
        "last_target_core",
        "last_timestamp",
    ],
    "authority": {
        "allowed": [
            "validate_runtime_eligibility",
            "resolve_declared_execution_surface",
            "invoke_declared_execution_handler",
            "emit_runtime_receipt",
            "terminate_invalid_propagation",
        ],
        "disallowed": [
            "create_strategy",
            "rewrite_pm_routing",
            "rewrite_pm_dispatch",
            "rewrite_ingress_state",
            "build_final_outputs",
            "run_watcher_logic",
            "update_smi_or_continuity_state",
            "coordinate_multi_core_workflows",
            "mutate_canon",
        ],
    },
}