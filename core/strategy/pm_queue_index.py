from AI_GO.core.strategy.pm_queue_index_policy import (
    build_index_payload,
    validate_output_index,
)


def build_pm_queue_index(
    pm_queue_records: list[dict],
    index_id: str,
    filters: dict | None = None,
    limit: int | None = None,
) -> dict:
    """
    Build one sealed pm_queue_index from multiple sealed pm_queue_record artifacts.

    This function preserves the separation between PM queue placement and
    PM queue retrieval structure. It does not mutate runtime behavior or PM queue truth.
    """
    payload = build_index_payload(
        pm_queue_records=pm_queue_records,
        index_id=index_id,
        filters=filters,
        limit=limit,
    )
    validate_output_index(payload)
    return payload