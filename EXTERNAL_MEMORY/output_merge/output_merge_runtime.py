from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Tuple

from .output_merge_receipt_builder import (
    build_output_merge_receipt,
    build_output_merge_rejection_receipt,
)
from .output_merge_registry import OUTPUT_MERGE_REGISTRY


def _validate_inputs(
    operator_response: Dict[str, Any],
    return_packet: Dict[str, Any],
    return_receipt: Dict[str, Any],
) -> Tuple[bool, str, str]:
    if not isinstance(operator_response, dict):
        return False, "invalid_operator_response", "operator_response_not_dict"

    if return_packet.get("artifact_type") != OUTPUT_MERGE_REGISTRY["accepted_return_packet_type"]:
        return False, "invalid_return_packet_type", "return_packet_type_not_allowed"

    if return_receipt.get("artifact_type") != OUTPUT_MERGE_REGISTRY["accepted_return_receipt_type"]:
        return False, "invalid_return_receipt_type", "return_receipt_type_not_allowed"

    if str(return_packet.get("requester_profile", "")) != str(return_receipt.get("requester_profile", "")):
        return False, "artifact_receipt_misalignment", "requester_profile_mismatch"

    if str(return_packet.get("target_child_core", "")) != str(return_receipt.get("target_child_core", "")):
        return False, "artifact_receipt_misalignment", "target_child_core_mismatch"

    advisory_summary = return_packet.get("advisory_summary", {})
    memory_context_panel = return_packet.get("memory_context_panel", {})
    if advisory_summary.get("state") != "present":
        return False, "missing_required_advisory_fields", "advisory_summary_state_missing"

    if memory_context_panel.get("state") != "present":
        return False, "missing_required_advisory_fields", "memory_context_panel_state_missing"

    return True, "", ""


def merge_external_memory_into_operator_output(
    operator_response: Dict[str, Any],
    return_packet: Dict[str, Any],
    return_receipt: Dict[str, Any],
) -> Dict[str, Any]:
    valid, failure_reason, detail = _validate_inputs(
        operator_response=operator_response,
        return_packet=return_packet,
        return_receipt=return_receipt,
    )
    if not valid:
        return {
            "status": "failed",
            "merged_response": None,
            "receipt": build_output_merge_rejection_receipt(
                failure_reason=failure_reason,
                detail=detail,
            ),
        }

    merged = deepcopy(operator_response)
    cognition_panel = merged.get("cognition_panel")
    if not isinstance(cognition_panel, dict):
        cognition_panel = {}
        merged["cognition_panel"] = cognition_panel

    merged["external_memory_merge_status"] = "merged"
    merged["external_memory_return_panel"] = deepcopy(return_packet["memory_context_panel"])
    merged["external_memory_provenance_refs"] = deepcopy(return_packet.get("provenance_refs", []))
    cognition_panel["external_memory_advisory"] = deepcopy(return_packet["advisory_summary"])

    receipt = build_output_merge_receipt(
        target_child_core=str(return_packet["target_child_core"]),
        requester_profile=str(return_packet["requester_profile"]),
        projection_targets=OUTPUT_MERGE_REGISTRY["allowed_projection_targets"],
    )
    return {
        "status": "ok",
        "merged_response": merged,
        "receipt": receipt,
    }