PM_CONTINUITY_REGISTRY = {
    "core_id": "pm_continuity_v1",
    "layer_status": "active",
    "accepted_input_artifact_type": "refinement_packet",
    "accepted_input_artifact_version": "v1",
    "emitted_record_artifact_type": "pm_continuity_record",
    "emitted_record_artifact_version": "v1",
    "emitted_index_artifact_type": "pm_continuity_index",
    "emitted_index_artifact_version": "v1",
    "approved_index_key_fields": [
        "core_id",
        "signal_class",
        "arbitration_class",
        "confidence_adjustment",
    ],
    "required_refinement_flags": {
        "execution_influence": False,
        "recommendation_mutation_allowed": False,
    },
    "required_output_flags": {
        "memory_only": True,
        "runtime_mutation_allowed": False,
    },
    "forbidden_internal_fields": [
        "_internal",
        "_debug",
        "_trace",
        "_raw_runtime_state",
        "_unsealed_source",
    ],
}