CHILD_CORE_INTAKE_REGISTRY = {
    "stage_id": 55,
    "stage_name": "child_core_intake_receipt",
    "authority_class": "runtime_child_core_boundary_acknowledgement",
    "module": "AI_GO.core.runtime.child_intake.child_core_intake_receipt",
    "entrypoint": "build_child_core_intake_receipt",
    "accepted_inputs": [
        "child_core_dispatch_packet",
    ],
    "required_inputs": [
        "child_core_dispatch_packet",
        "intake_decision",
    ],
    "optional_inputs": [
        "intake_reason",
        "accepted_by",
    ],
    "emitted_artifact": "child_core_intake_receipt",
    "approved_targets": [
        "proposal_saas",
        "gis",
        "wru",
    ],
    "approved_intake_decisions": [
        "accepted",
        "rejected",
    ],
    "forbidden_behaviors": [
        "truth_re_resolution",
        "dispatch_re_routing",
        "child_core_execution",
        "dispatch_packet_mutation",
        "implicit_intake_acceptance",
        "multi_target_acknowledgement",
    ],
    "invariants": [
        "child_core_dispatch_packet is required",
        "dispatch packet must be sealed and dispatch_ready",
        "target_child_core must be approved",
        "intake_decision must be explicit",
        "rejection requires intake_reason",
        "one child_core_intake_receipt is emitted",
        "output is acknowledgement only",
        "no domain execution is performed",
    ],
}