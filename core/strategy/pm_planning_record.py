from AI_GO.core.strategy.pm_planning_policy import (
    build_planning_payload,
    validate_output_planning,
    validate_pm_review_record,
)


def build_pm_planning_record(
    pm_review_record: dict,
    planning_id: str,
) -> dict:
    """
    Build one sealed pm_planning_record from one sealed pm_review_record.

    This function preserves the separation between PM review posture and
    PM workflow preparation. It does not mutate runtime behavior or PM review truth.
    """
    validate_pm_review_record(pm_review_record)
    payload = build_planning_payload(
        pm_review_record=pm_review_record,
        planning_id=planning_id,
    )
    validate_output_planning(payload)
    return payload