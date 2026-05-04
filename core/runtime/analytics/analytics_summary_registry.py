ANALYTICS_SUMMARY_REGISTRY = {
    "stage_id": 60,
    "stage_name": "analytics_summary",
    "authority_class": "runtime_descriptive_analytics",
    "module": "AI_GO.core.runtime.analytics.analytics_summary",
    "entrypoint": "build_analytics_summary",
    "accepted_inputs": [
        "archive_retrieval_result",
    ],
    "required_inputs": [
        "archive_retrieval_result",
    ],
    "optional_inputs": [],
    "emitted_artifact": "analytics_summary",
    "approved_count_dimensions": [
        "artifact_type",
        "closeout_state",
        "final_state",
        "intake_decision",
        "target_child_core",
    ],
    "forbidden_behaviors": [
        "mutation",
        "execution",
        "truth_inference",
        "learning",
        "reweighting",
        "internal_field_exposure",
    ],
    "invariants": [
        "input must be a sealed archive_retrieval_result",
        "results must remain approved finalized artifact types",
        "output is descriptive analytics only",
        "no source artifacts are mutated",
        "no learning or refinement is performed",
    ],
}