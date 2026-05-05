from __future__ import annotations

APPROVED_INPUT_ARTIFACT_TYPE = "execution_fusion_record"
APPROVED_OUTPUT_ARTIFACT_TYPE = "child_core_execution_packet"

APPROVED_CHILD_CORE_TARGETS = {
    "market_analyzer_v1": {
        "target_core": "market_analyzer_v1",
        "required_payload_type": "dict",
        "required_handoff_posture": "child_core_ready",
    }
}

REQUIRED_FUSION_KEYS = {
    "artifact_type",
    "sealed",
    "fusion_id",
    "runtime_mode",
    "combined_weights",
}

REQUIRED_WEIGHT_KEYS = {
    "combined_weight",
    "rosetta_weight",
    "curved_mirror_weight",
}

REQUIRED_RUNTIME_MODE_KEYS = {
    "mode",
}

APPROVED_HANDOFF_POSTURE_VALUES = {
    "child_core_ready",
}

APPROVED_INTAKE_STATUS_VALUES = {
    "accepted",
}

APPROVED_DOWNSTREAM_STATUS_VALUES = {
    "ready_for_execution_surface",
}

FORBIDDEN_INTERNAL_FIELDS = {
    "internal_notes",
    "private_reasoning",
    "hidden_weights",
    "adapter_override",
    "target_override",
}