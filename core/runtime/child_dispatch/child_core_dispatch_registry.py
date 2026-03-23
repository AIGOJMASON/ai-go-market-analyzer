CHILD_CORE_DISPATCH_REGISTRY = {
    "stage_id": 54,
    "stage_name": "child_core_dispatch",
    "authority_class": "runtime_child_core_dispatch",
    "module": "AI_GO.core.runtime.child_dispatch.child_core_dispatch",
    "entrypoint": "build_child_core_dispatch_packet",
    "accepted_inputs": [
        "case_resolution",
    ],
    "required_inputs": [
        "case_resolution",
        "target_child_core",
    ],
    "optional_inputs": [
        "dispatch_note",
    ],
    "emitted_artifact": "child_core_dispatch_packet",
    "approved_targets": [
        "proposal_saas",
        "gis",
        "wru",
    ],
    "forbidden_behaviors": [
        "truth_re_resolution",
        "raw_replay_consumption",
        "raw_receipt_consumption",
        "child_core_execution",
        "receipt_mutation",
        "resolution_mutation",
        "multi_target_dispatch",
        "implicit_target_invention",
    ],
    "invariants": [
        "case_resolution is required",
        "case_resolution must be sealed and actionable",
        "target_child_core must be approved",
        "payload_class and route_class must match target policy",
        "one child_core_dispatch_packet is emitted",
        "output is dispatch preparation only",
        "no domain execution is performed",
    ],
}