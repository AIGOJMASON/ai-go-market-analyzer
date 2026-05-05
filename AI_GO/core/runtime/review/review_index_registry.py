REVIEW_INDEX_REGISTRY = {
    "stage_id": 58,
    "stage_name": "operator_review_index",
    "authority_class": "runtime_review_query",
    "module": "AI_GO.core.runtime.review.review_index",
    "entrypoint": "build_operator_review_index",
    "accepted_inputs": ["operator_review_view[]"],
    "required_inputs": ["operator_review_view[]"],
    "emitted_artifact": "operator_review_index",
    "forbidden_behaviors": [
        "mutation",
        "execution",
        "truth_inference",
        "internal_field_exposure",
    ],
    "invariants": [
        "all inputs must be sealed",
        "all inputs must be operator_review_view",
        "output is bounded projection",
        "pagination enforced",
    ],
}