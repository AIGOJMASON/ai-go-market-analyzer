OPERATOR_REVIEW_REGISTRY = {
    "stage_id": 57,
    "stage_name": "operator_review_view",
    "authority_class": "runtime_operator_projection",
    "module": "AI_GO.core.runtime.review.operator_review_view",
    "entrypoint": "build_operator_review_view",
    "accepted_inputs": ["case_closeout_record"],
    "required_inputs": ["case_closeout_record"],
    "emitted_artifact": "operator_review_view",
    "forbidden_behaviors": [
        "truth_mutation",
        "execution_trigger",
        "state_inference",
        "internal_field_exposure",
    ],
    "invariants": [
        "input must be sealed",
        "input must be case_closeout_record",
        "output is projection only",
        "no mutation of source artifact",
    ],
}