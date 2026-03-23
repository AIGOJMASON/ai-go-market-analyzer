AUDIT_REPLAY_REGISTRY = {
    "stage_id": 52,
    "stage_name": "audit_replay_index",
    "authority_class": "runtime_structural_consolidation",
    "module": "AI_GO.core.runtime.audit.audit_replay_index",
    "entrypoint": "build_audit_replay_index",
    "accepted_inputs": [
        "delivery_outcome_receipt",
        "retry_outcome_receipt",
        "escalation_outcome_receipt",
    ],
    "required_inputs": [
        "delivery_outcome_receipt",
    ],
    "optional_inputs": [
        "retry_outcome_receipt",
        "escalation_outcome_receipt",
    ],
    "emitted_artifact": "audit_replay_index",
    "forbidden_behaviors": [
        "execution",
        "retry_execution",
        "escalation_execution",
        "final_state_resolution",
        "child_core_dispatch",
        "receipt_mutation",
        "implicit_branch_synthesis",
    ],
    "invariants": [
        "delivery_outcome_receipt is required",
        "all provided receipts must share one case_id",
        "one receipt per branch_class",
        "internal field leakage is blocked",
        "output is structural replay only",
        "no final truth is declared",
    ],
}