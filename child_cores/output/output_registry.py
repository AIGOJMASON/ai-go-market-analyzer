from __future__ import annotations

from typing import Dict, Tuple

OUTPUT_STAGE_ID = "stage23_child_core_output"

DISALLOWED_AUTHORITIES: Tuple[str, ...] = (
    "publication",
    "watcher_trigger",
    "continuity_mutation",
    "runtime_reinvocation",
    "pm_state_mutation",
    "canon_state_mutation",
    "multi_core_coordination",
)

DECLARED_OUTPUT_SURFACES: Dict[str, str] = {
    "contractor_proposals_core": "output.proposal_artifact",
    "louisville_gis_core": "output.gis_artifact",
}


def runtime_result_to_payload(
    runtime_receipt: dict,
    output_context: dict,
) -> dict:
    """
    Default bounded builder for child-core outputs.

    This builder intentionally stays small. It constructs a compact payload
    from runtime facts and optional bounded context flags only.
    """
    payload = {
        "target_core": runtime_receipt["target_core"],
        "runtime_id": runtime_receipt["runtime_id"],
        "result_ref": runtime_receipt.get("result_ref"),
    }

    output_flags = output_context.get("output_flags")
    if output_flags is not None:
        payload["output_flags"] = output_flags

    input_refs = output_context.get("input_refs")
    if input_refs is not None:
        payload["input_refs"] = input_refs

    return payload


OUTPUT_BUILDERS = {
    "contractor_proposals_core": runtime_result_to_payload,
    "louisville_gis_core": runtime_result_to_payload,
}