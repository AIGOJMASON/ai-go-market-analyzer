from copy import deepcopy

from AI_GO.core.pm_continuity.pm_continuity_policy import (
    build_base_record,
    build_continuity_key,
    validate_output_record,
    validate_refinement_packet,
)


def build_pm_continuity_record(
    refinement_packet: dict,
    record_id: str,
) -> dict:
    """
    Build one sealed pm_continuity_record from one sealed refinement_packet.

    This function preserves refinement truth as PM continuity memory.
    It does not re-score, re-arbitrate, or mutate runtime behavior.
    """
    validate_refinement_packet(refinement_packet)

    continuity_key = build_continuity_key(refinement_packet)
    record = build_base_record(
        refinement_packet=deepcopy(refinement_packet),
        record_id=record_id,
        continuity_key=continuity_key,
    )

    validate_output_record(record)
    return record