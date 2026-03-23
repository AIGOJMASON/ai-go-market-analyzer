"""
Registry definition for Stage 73 execution fusion.
"""

from __future__ import annotations

APPROVED_INPUT_ARTIFACT_TYPES = {
    "rosetta": "rosetta_runtime_execution_state",
    "curved_mirror": "curved_mirror_runtime_execution_state",
}

EMITTED_ARTIFACT_TYPE = "execution_fusion_record"

APPROVED_DOWNSTREAM_STATUS = {
    "ready_for_child_core",
}

APPROVED_CHILD_CORE_HANDOFF = {
    "fused_execution_ready",
}

REQUIRED_EXECUTION_STATE_KEYS = {
    "artifact_type",
    "sealed",
    "case_id",
    "authorized_weight",
    "refinement_entry_count",
    "runtime_mode",
    "downstream_status",
}

FORBIDDEN_INTERNAL_KEYS = {
    "_debug",
    "_trace",
    "_internal",
    "_private",
    "internal_state",
    "internal_notes",
    "hidden_fields",
}

REGISTRY = {
    "stage": 73,
    "layer_name": "execution_fusion",
    "accepted_inputs": APPROVED_INPUT_ARTIFACT_TYPES,
    "emitted_artifact_type": EMITTED_ARTIFACT_TYPE,
    "approved_downstream_status": sorted(APPROVED_DOWNSTREAM_STATUS),
    "approved_child_core_handoff": sorted(APPROVED_CHILD_CORE_HANDOFF),
    "required_execution_state_keys": sorted(REQUIRED_EXECUTION_STATE_KEYS),
    "forbidden_internal_keys": sorted(FORBIDDEN_INTERNAL_KEYS),
}