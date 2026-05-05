CASE_RESOLUTION_REGISTRY = {
    "stage_id": 53,
    "stage_name": "case_resolution",
    "authority_class": "runtime_final_state_resolution",
    "module": "AI_GO.core.runtime.resolution.case_resolution",
    "entrypoint": "build_case_resolution",
    "accepted_inputs": [
        "audit_replay_index",
    ],
    "required_inputs": [
        "audit_replay_index",
    ],
    "optional_inputs": [],
    "emitted_artifact": "case_resolution",
    "forbidden_behaviors": [
        "execution",
        "retry_execution",
        "escalation_execution",
        "child_core_dispatch",
        "receipt_mutation",
        "replay_mutation",
        "implicit_branch_synthesis",
        "multi_state_resolution",
    ],
    "invariants": [
        "audit_replay_index is required",
        "replay_chain must not be empty",
        "replay_chain must begin with primary",
        "one entry per branch_class",
        "one exclusive final_state is emitted",
        "output is final-state resolution only",
        "no child-core routing is declared",
    ],
}