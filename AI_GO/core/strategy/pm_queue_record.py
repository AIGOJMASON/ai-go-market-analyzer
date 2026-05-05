from AI_GO.core.strategy.pm_queue_policy import (
    build_queue_payload,
    validate_output_queue,
    validate_pm_planning_record,
)


def build_pm_queue_record(
    pm_planning_record: dict,
    queue_id: str,
) -> dict:
    """
    Build one sealed pm_queue_record from one sealed pm_planning_record.

    This function preserves the separation between PM planning posture and
    PM workflow placement. It does not mutate runtime behavior or PM planning truth.
    """
    validate_pm_planning_record(pm_planning_record)
    payload = build_queue_payload(
        pm_planning_record=pm_planning_record,
        queue_id=queue_id,
    )
    validate_output_queue(payload)
    return payload