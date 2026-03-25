PM_QUEUE_REGISTRY = {
    "core_id": "pm_queue_v1",
    "layer_status": "active",
    "accepted_planning_artifact_type": "pm_planning_record",
    "accepted_planning_artifact_version": "v1",
    "emitted_queue_artifact_type": "pm_queue_record",
    "emitted_queue_artifact_version": "v1",
    "approved_queue_lanes": [
        "pm_hold_queue",
        "pm_review_queue",
        "pm_planning_queue",
        "pm_escalation_queue",
    ],
    "approved_queue_status_values": [
        "held",
        "queued",
    ],
    "approved_queue_target_values": [
        "observe",
        "review",
        "planning",
        "escalation",
    ],
    "approved_queue_priority_values": [
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
    "queue_scope": "pm_queue_only",
    "forbidden_internal_fields": [
        "_internal",
        "_debug",
        "_trace",
        "_raw_runtime_state",
        "_unsealed_source",
    ],
}