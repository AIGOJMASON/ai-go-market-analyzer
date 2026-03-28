# MARKET ANALYZER EXTERNAL MEMORY RETURN PATH INTEGRATION

Purpose:
Define the bounded return-path hook that allows market_analyzer_v1 to convert
promoted external memory into advisory-ready packet form for safe live output
projection.

Rule:
Return-path output is advisory only.

Suggested Return-Path Call:
run_market_analyzer_external_memory_return_path(
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
    "artifact_type": "external_memory_return_packet",
    "requester_profile": "...",
    "target_child_core": "market_analyzer_v1",
    "promotion_score": ...,
    "record_count": ...,
    "advisory_summary": {...},
    "memory_context_panel": {...},
    "provenance_refs": [...]
  } | None,
  "receipt": {
    "artifact_type": "external_memory_return_receipt"
    ...
  } | {
    "artifact_type": "external_memory_return_rejection_receipt"
    ...
  }
}

Allowed Live Projection:
This packet may be projected into market analyzer live output as:
- external_memory_return_panel
- memory_context_panel
- advisory context note

It may not:
- rewrite recommendation logic
- change runtime execution
- change PM strategy
- silently adjust confidence

Phase 4 Limitation:
Return-path output is packetized advisory context only.
A later integration layer may decide how it is merged into final operator
response surfaces.