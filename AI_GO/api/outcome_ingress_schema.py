from __future__ import annotations

ALLOWED_OUTCOME_INGRESS_SOURCES = {
    "manual",
    "api",
    "market_feed",
    "external_feed",
}


def build_outcome_ingress_request(
    *,
    closeout_id: str,
    actual_outcome: str,
    source: str = "manual",
    notes: str = "",
    observed_at: str | None = None,
) -> dict:
    return {
        "closeout_id": closeout_id,
        "actual_outcome": actual_outcome,
        "source": source,
        "notes": notes,
        "observed_at": observed_at,
    }