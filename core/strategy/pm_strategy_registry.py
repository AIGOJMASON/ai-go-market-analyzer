
PM_STRATEGY_REGISTRY = {
    "core_id": "pm_strategy_v1",
    "layer_status": "active",
    "accepted_record_artifact_type": "pm_continuity_record",
    "accepted_record_artifact_version": "v1",
    "accepted_index_artifact_type": "pm_continuity_index",
    "accepted_index_artifact_version": "v1",
    "emitted_strategy_artifact_type": "pm_strategy_record",
    "emitted_strategy_artifact_version": "v1",
    "approved_strategy_classes": [
        "monitor",
        "elevated_caution",
        "reinforced_support",
        "insufficient_pattern",
        "escalate_for_pm_review",
    ],
    "approved_continuity_strength_values": [
        "low",
        "medium",
        "high",
    ],
    "approved_trend_direction_values": [
        "reinforcing",
        "branching",
        "mixed",
        "insufficient_data",
    ],
    "required_input_flags": {
        "memory_only": True,
        "runtime_mutation_allowed": False,
    },
    "required_record_flags": {
        "execution_influence": False,
        "recommendation_mutation_allowed": False,
    },
    "required_output_flags": {
        "memory_only": True,
        "runtime_mutation_allowed": False,
        "execution_influence": False,
        "recommendation_mutation_allowed": False,
    },
    "strategy_scope": "pm_guidance_only",
    "forbidden_internal_fields": [
        "_internal",
        "_debug",
        "_trace",
        "_raw_runtime_state",
        "_unsealed_source",
    ],
}