"""
Registry definition for Stage 70 runtime refinement coupling.
"""

from __future__ import annotations

APPROVED_INPUT_ARTIFACT_TYPES = {
    "allocation": "engine_allocation_record",
    "rosetta_receipt": "rosetta_refinement_receipt",
    "curved_mirror_receipt": "curved_mirror_refinement_receipt",
}

EMITTED_ARTIFACT_TYPE = "runtime_refinement_coupling_record"

APPROVED_ROUTE_TARGETS = {
    "rosetta": "stage71_rosetta_runtime_application",
    "curved_mirror": "stage72_curved_mirror_runtime_application",
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

REQUIRED_ALLOCATION_KEYS = {
    "artifact_type",
    "sealed",
    "case_id",
    "rosetta_weight",
    "curved_mirror_weight",
}

REQUIRED_RECEIPT_KEYS = {
    "artifact_type",
    "sealed",
    "case_id",
}

OPTIONAL_ENTRY_KEYS = {
    "entries",
    "guidance",
    "signals",
    "notes",
}

REGISTRY = {
    "stage": 70,
    "layer_name": "runtime_refinement_coupler",
    "accepted_inputs": APPROVED_INPUT_ARTIFACT_TYPES,
    "emitted_artifact_type": EMITTED_ARTIFACT_TYPE,
    "approved_route_targets": APPROVED_ROUTE_TARGETS,
    "forbidden_internal_keys": sorted(FORBIDDEN_INTERNAL_KEYS),
    "required_allocation_keys": sorted(REQUIRED_ALLOCATION_KEYS),
    "required_receipt_keys": sorted(REQUIRED_RECEIPT_KEYS),
}