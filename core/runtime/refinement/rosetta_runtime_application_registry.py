"""
Registry definition for Stage 71 Rosetta runtime application.
"""

from __future__ import annotations

APPROVED_INPUT_ARTIFACT_TYPE = "runtime_refinement_coupling_record"
EMITTED_ARTIFACT_TYPE = "rosetta_runtime_execution_state"

APPROVED_ROUTE_TARGET = "stage71_rosetta_runtime_application"

APPROVED_RUNTIME_MODES = {
    "rosetta_refined_runtime",
}

APPROVED_DOWNSTREAM_STATUS = {
    "ready_for_child_core",
}

REQUIRED_INPUT_KEYS = {
    "artifact_type",
    "sealed",
    "case_id",
    "allocation",
    "rosetta_channel",
    "curved_mirror_channel",
}

REQUIRED_ROSETTA_CHANNEL_KEYS = {
    "authorized_weight",
    "route_target",
    "receipt_artifact_type",
    "entry_count",
    "sealed_receipt",
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
    "stage": 71,
    "layer_name": "rosetta_runtime_application",
    "accepted_input": APPROVED_INPUT_ARTIFACT_TYPE,
    "emitted_artifact_type": EMITTED_ARTIFACT_TYPE,
    "approved_route_target": APPROVED_ROUTE_TARGET,
    "approved_runtime_modes": sorted(APPROVED_RUNTIME_MODES),
    "approved_downstream_status": sorted(APPROVED_DOWNSTREAM_STATUS),
    "required_input_keys": sorted(REQUIRED_INPUT_KEYS),
    "required_rosetta_channel_keys": sorted(REQUIRED_ROSETTA_CHANNEL_KEYS),
    "forbidden_internal_keys": sorted(FORBIDDEN_INTERNAL_KEYS),
}