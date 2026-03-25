from AI_GO.core.strategy.pm_strategy_policy import (
    build_strategy_payload,
    validate_output_strategy,
    validate_pm_continuity_index,
    validate_pm_continuity_record,
)


def build_pm_strategy_record(
    pm_continuity_record: dict,
    pm_continuity_index: dict,
    strategy_id: str,
) -> dict:
    """
    Build one sealed pm_strategy_record from one sealed pm_continuity_record
    and one sealed pm_continuity_index.

    This function preserves the separation between continuity memory and PM
    strategy guidance. It does not mutate runtime behavior or continuity truth.
    """
    validate_pm_continuity_record(pm_continuity_record)
    validate_pm_continuity_index(pm_continuity_index)

    if pm_continuity_record["core_id"] != pm_continuity_index["entries"][0]["core_id"] if pm_continuity_index["entries"] else pm_continuity_record["core_id"]:
        # If the index is empty, this passes trivially.
        # If it has entries, they must belong to the same core family.
        raise ValueError("core_id mismatch between continuity record and continuity index")

    payload = build_strategy_payload(
        pm_continuity_record=pm_continuity_record,
        pm_continuity_index=pm_continuity_index,
        strategy_id=strategy_id,
    )
    validate_output_strategy(payload)
    return payload