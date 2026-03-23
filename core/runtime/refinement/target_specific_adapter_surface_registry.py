"""
Registry definition for Stage 77 target-specific adapter surface.
"""

from __future__ import annotations

APPROVED_INPUT_ARTIFACT_TYPE = "child_core_adapter_packet"
EMITTED_ARTIFACT_TYPE = "target_specific_adapter_packet"

APPROVED_CHILD_CORE_TARGETS = {
    "proposal_builder",
    "gis",
    "white_raven_university",
    "writing_core",
}

APPROVED_ADAPTER_CLASSES = {
    "proposal_adapter",
    "gis_adapter",
    "education_adapter",
    "writing_adapter",
}

TARGET_TO_ADAPTER_CLASS = {
    "proposal_builder": "proposal_adapter",
    "gis": "gis_adapter",
    "white_raven_university": "education_adapter",
    "writing_core": "writing_adapter",
}

TARGET_TO_SURFACE_CLASS = {
    "proposal_builder": "proposal_target_surface",
    "gis": "gis_target_surface",
    "white_raven_university": "education_target_surface",
    "writing_core": "writing_target_surface",
}

APPROVED_ADAPTER_STATUS = {
    "ready_for_target_adapter",
}

APPROVED_DOWNSTREAM_STATUS = {
    "ready_for_result_handling",
}

APPROVED_TARGET_SPECIFIC_STATUS = {
    "ready_for_target_implementation",
}

REQUIRED_PACKET_KEYS = {
    "artifact_type",
    "sealed",
    "case_id",
    "source_artifact_type",
    "child_core_target",
    "adapter_class",
    "weights",
    "runtime_modes",
    "adapter_status",
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
    "stage": 77,
    "layer_name": "target_specific_adapter_surface",
    "accepted_input": APPROVED_INPUT_ARTIFACT_TYPE,
    "emitted_artifact_type": EMITTED_ARTIFACT_TYPE,
    "approved_child_core_targets": sorted(APPROVED_CHILD_CORE_TARGETS),
    "approved_adapter_classes": sorted(APPROVED_ADAPTER_CLASSES),
    "target_to_adapter_class": TARGET_TO_ADAPTER_CLASS,
    "target_to_surface_class": TARGET_TO_SURFACE_CLASS,
    "approved_adapter_status": sorted(APPROVED_ADAPTER_STATUS),
    "approved_downstream_status": sorted(APPROVED_DOWNSTREAM_STATUS),
    "approved_target_specific_status": sorted(APPROVED_TARGET_SPECIFIC_STATUS),
    "required_packet_keys": sorted(REQUIRED_PACKET_KEYS),
    "required_weight_keys": sorted(REQUIRED_WEIGHT_KEYS),
    "required_runtime_mode_keys": sorted(REQUIRED_RUNTIME_MODE_KEYS),
    "forbidden_internal_keys": sorted(FORBIDDEN_INTERNAL_KEYS),
}