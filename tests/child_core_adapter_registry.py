"""
Registry definition for Stage 76 child-core adapter layer.
"""

from __future__ import annotations

APPROVED_INPUT_ARTIFACT_TYPE = "child_core_execution_result"
EMITTED_ARTIFACT_TYPE = "child_core_adapter_packet"

APPROVED_CHILD_CORE_TARGETS = {
    "proposal_builder",
    "gis",
    "white_raven_university",
    "writing_core",
}

TARGET_TO_ADAPTER_CLASS = {
    "proposal_builder": "proposal_adapter",
    "gis": "gis_adapter",
    "white_raven_university": "education_adapter",
    "writing_core": "writing_adapter",
}

APPROVED_EXECUTION_STATUS = {
    "execution_surface_complete",
}

APPROVED_DOWNSTREAM_STATUS = {
    "ready_for_result_handling",
}

APPROVED_ADAPTER_STATUS = {
    "ready_for_target_adapter",
}

REQUIRED_RESULT_KEYS = {
    "artifact_type",
    "sealed",
    "case_id",
    "source_artifact_type",
    "child_core_target",
    "weights",
    "runtime_modes",
    "execution_status",
    "downstream_status",
}

REQUIRED_WEIGHT_KEYS = {
    "rosetta_weight",
    "curved_mirror_weight",
}

REQUIRED_RUNTIME_MODE_KEYS = {
    "rosetta_mode",
    "curved_mirror_mode",
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
    "stage": 76,
    "layer_name": "child_core_adapter",
    "accepted_input": APPROVED_INPUT_ARTIFACT_TYPE,
    "emitted_artifact_type": EMITTED_ARTIFACT_TYPE,
    "approved_child_core_targets": sorted(APPROVED_CHILD_CORE_TARGETS),
    "target_to_adapter_class": TARGET_TO_ADAPTER_CLASS,
    "approved_execution_status": sorted(APPROVED_EXECUTION_STATUS),
    "approved_downstream_status": sorted(APPROVED_DOWNSTREAM_STATUS),
    "approved_adapter_status": sorted(APPROVED_ADAPTER_STATUS),
    "required_result_keys": sorted(REQUIRED_RESULT_KEYS),
    "required_weight_keys": sorted(REQUIRED_WEIGHT_KEYS),
    "required_runtime_mode_keys": sorted(REQUIRED_RUNTIME_MODE_KEYS),
    "forbidden_internal_keys": sorted(FORBIDDEN_INTERNAL_KEYS),
}