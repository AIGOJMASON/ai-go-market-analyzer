from __future__ import annotations

APPROVED_INPUT_ARTIFACT_TYPE = "child_core_execution_result"
APPROVED_OUTPUT_ARTIFACT_TYPE = "child_core_adapter_packet"

APPROVED_CHILD_CORE_TARGETS = {
    "market_analyzer_v1": {
        "target_core": "market_analyzer_v1",
        "adapter_class": "market_analyzer_adapter",
        "target_surface_class": "market_analyzer_surface",
    }
}

REQUIRED_EXECUTION_RESULT_KEYS = {
    "artifact_type",
    "sealed",
    "result_id",
    "source_artifact_type",
    "source_lineage",
    "target_core",
    "execution_status",
    "downstream_status",
    "runtime_mode",
    "combined_weights",
    "execution_artifacts",
    "runtime_error",
    "receipt",
}

REQUIRED_WEIGHT_KEYS = {
    "combined_weight",
    "rosetta_weight",
    "curved_mirror_weight",
}

REQUIRED_RUNTIME_MODE_KEYS = {
    "mode",
}

APPROVED_EXECUTION_STATUS_VALUES = {
    "succeeded",
    "rejected",
}

APPROVED_DOWNSTREAM_STATUS_INPUT_VALUES = {
    "ready_for_adapter",
    "execution_rejected",
}

APPROVED_ADAPTER_STATUS_VALUES = {
    "adapted",
    "rejected",
}

APPROVED_DOWNSTREAM_STATUS_OUTPUT_VALUES = {
    "ready_for_target_surface",
    "adapter_rejected",
}

FORBIDDEN_INTERNAL_FIELDS = {
    "internal_notes",
    "private_reasoning",
    "hidden_weights",
    "adapter_override",
    "target_override",
}