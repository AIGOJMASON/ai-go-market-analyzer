# MARKET ANALYZER EXTERNAL MEMORY PROMOTION INTEGRATION

Purpose:
Define the bounded promotion hook that allows market_analyzer_v1 to evaluate
retrieved external-memory records for reusable advisory status without yet
feeding them back into live output.

Rule:
Promotion is advisory-ready, not runtime-authoritative.

Suggested Promotion Call:
run_market_analyzer_external_memory_promotion(
    limit=10,
    source_type=None,
    trust_class=None,
    min_adjusted_weight=None,
    symbol=None,
    sector=None,
    requester_profile="market_analyzer_reader",
)

Expected Return:
{
  "status": "ok" | "failed",
  "artifact": {
    "artifact_type": "external_memory_promotion_artifact",
    "requester_profile": "...",
    "target_child_core": "market_analyzer_v1",
    "decision": "promoted" | "hold",
    "promotion_score": ...,
    "record_count": ...,
    "coherence_flags": [...],
    "promoted_records": [...],
    "rationale": {...},
    "advisory_summary": {...}
  } | None,
  "receipt": {
    "artifact_type": "external_memory_promotion_receipt"
    ...
  } | {
    "artifact_type": "external_memory_promotion_rejection_receipt"
    ...
  }
}

Phase 3 Limitation:
Promotion does not yet:
- alter live recommendation state
- alter PM influence
- mutate runtime confidence
- bypass later return-path integration

Promotion only establishes:
- what retrieved memory is strong enough to matter later
- what remains too weak for reuse