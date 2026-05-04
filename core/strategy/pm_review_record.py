from AI_GO.core.strategy.pm_review_policy import (
    build_review_payload,
    validate_output_review,
    validate_pm_strategy_record,
)


def build_pm_review_record(
    pm_strategy_record: dict,
    review_id: str,
) -> dict:
    """
    Build one sealed pm_review_record from one sealed pm_strategy_record.

    This function preserves the separation between PM strategy guidance and
    PM-facing review. It does not mutate runtime behavior or PM strategy truth.
    """
    validate_pm_strategy_record(pm_strategy_record)
    payload = build_review_payload(
        pm_strategy_record=pm_strategy_record,
        review_id=review_id,
    )
    validate_output_review(payload)
    return payload