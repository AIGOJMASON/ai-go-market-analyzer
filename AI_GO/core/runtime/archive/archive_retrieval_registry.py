ARCHIVE_RETRIEVAL_REGISTRY = {
    "stage_id": 59,
    "stage_name": "archive_retrieval_result",
    "authority_class": "runtime_archive_retrieval",
    "module": "AI_GO.core.runtime.archive.archive_retrieval",
    "entrypoint": "build_archive_retrieval_result",
    "accepted_inputs": [
        "case_closeout_record[]",
        "operator_review_view[]",
        "operator_review_index[]",
    ],
    "required_inputs": [
        "archive_items",
    ],
    "optional_inputs": [
        "filters",
        "limit",
        "offset",
    ],
    "emitted_artifact": "archive_retrieval_result",
    "approved_filter_fields": [
        "artifact_type",
        "case_id",
        "target_child_core",
        "closeout_state",
        "final_state",
        "intake_decision",
    ],
    "forbidden_behaviors": [
        "mutation",
        "execution",
        "truth_inference",
        "reopen_case",
        "internal_field_exposure",
    ],
    "invariants": [
        "all archive items must be sealed",
        "all archive items must be approved finalized artifact types",
        "filters may only use approved fields",
        "output is bounded retrieval only",
        "pagination must remain explicit and deterministic",
    ],
}