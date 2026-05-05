PM_REVIEW_REGISTRY = {
    "core_id": "pm_review_v1",
    "layer_status": "active",
    "accepted_strategy_artifact_type": "pm_strategy_record",
    "accepted_strategy_artifact_version": "v1",
    "emitted_review_artifact_type": "pm_review_record",
    "emitted_review_artifact_version": "v1",
    "approved_review_classes": [
        "observe",
        "review",
        "plan",
        "escalate",
    ],
    "approved_review_priority_values": [
        "low",
        "medium",
        "high",
    ],
    "required_input_flags": {
        "memory_only": True,
        "runtime_mutation_allowed": False,
        "execution_influence": False,
        "recommendation_mutation_allowed": False,
    },
    "required_output_flags": {
        "memory_only": True,
        "runtime_mutation_allowed": False,
        "execution_influence": False,
        "recommendation_mutation_allowed": False,
    },
    "review_scope": "pm_review_only",
    "forbidden_internal_fields": [
        "_internal",
        "_debug",
        "_trace",
        "_raw_runtime_state",
        "_unsealed_source",
    ],
}