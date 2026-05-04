from AI_GO.core.strategy.pm_workflow_dispatch_policy import (
    build_dispatch_payload,
    ensure_queue_membership,
    validate_output_dispatch,
    validate_pm_queue_index,
    validate_pm_queue_record,
)


def build_pm_workflow_dispatch_record(
    pm_queue_record: dict,
    pm_queue_index: dict,
    dispatch_id: str,
) -> dict:
    """
    Build one sealed pm_workflow_dispatch_record from one sealed pm_queue_record
    plus one sealed pm_queue_index.

    This function preserves the separation between PM queue placement and
    PM workflow dispatch preparation. It does not mutate runtime behavior or PM queue truth.
    """
    validate_pm_queue_record(pm_queue_record)
    validate_pm_queue_index(pm_queue_index)
    ensure_queue_membership(pm_queue_record, pm_queue_index)

    payload = build_dispatch_payload(
        pm_queue_record=pm_queue_record,
        pm_queue_index=pm_queue_index,
        dispatch_id=dispatch_id,
    )
    validate_output_dispatch(payload)
    return payload