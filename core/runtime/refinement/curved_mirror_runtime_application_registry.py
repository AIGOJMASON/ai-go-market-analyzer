"""
Registry definition for Stage 72 Curved Mirror runtime application.
"""

from __future__ import annotations

APPROVED_INPUT_ARTIFACT_TYPE = "runtime_refinement_coupling_record"
EMITTED_ARTIFACT_TYPE = "curved_mirror_runtime_execution_state"

APPROVED_ROUTE_TARGET = "stage72_curved_mirror_runtime_application"

APPROVED_RUNTIME_MODES = {
    "curved_mirror_refined_runtime",
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

REQUIRED_CURVED_MIRROR_CHANNEL_KEYS = {
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
    "stage": 72,
    "layer_name": "curved_mirror_runtime_application",
    "accepted_input": APPROVED_INPUT_ARTIFACT_TYPE,
    "emitted_artifact_type": EMITTED_ARTIFACT_TYPE,
    "approved_route_target": APPROVED_ROUTE_TARGET,
    "approved_runtime_modes": sorted(APPROVED_RUNTIME_MODES),
    "approved_downstream_status": sorted(APPROVED_DOWNSTREAM_STATUS),
    "required_input_keys": sorted(REQUIRED_INPUT_KEYS),
    "required_curved_mirror_channel_keys": sorted(REQUIRED_CURVED_MIRROR_CHANNEL_KEYS),
    "forbidden_internal_keys": sorted(FORBIDDEN_INTERNAL_KEYS),
}