from __future__ import annotations

APPROVED_INPUT_ARTIFACT_TYPE = "child_core_execution_packet"
APPROVED_OUTPUT_ARTIFACT_TYPE = "child_core_execution_result"

APPROVED_CHILD_CORE_TARGETS = {
    "market_analyzer_v1": {
        "target_core": "market_analyzer_v1",
        "executor_module": "AI_GO.child_cores.market_analyzer_v1.execution.run",
        "executor_fn": "run",
    }
}

REQUIRED_PACKET_KEYS = {
    "artifact_type",
    "sealed",
    "packet_id",
    "target_core",
    "intake_status",
    "downstream_status",
    "runtime_mode",
    "combined_weights",
    "child_core_payload",
}

REQUIRED_WEIGHT_KEYS = {
    "combined_weight",
    "rosetta_weight",
    "curved_mirror_weight",
}

REQUIRED_RUNTIME_MODE_KEYS = {
    "mode",
}

APPROVED_INTAKE_VALUES = {
    "accepted",
}

APPROVED_EXECUTION_STATUS_VALUES = {
    "succeeded",
    "rejected",
}

APPROVED_DOWNSTREAM_STATUS_VALUES = {
    "ready_for_adapter",
    "execution_rejected",
}

FORBIDDEN_INTERNAL_FIELDS = {
    "internal_notes",
    "private_reasoning",
    "hidden_weights",
    "adapter_override",
    "target_override",
}