# MARKET ANALYZER EXTERNAL MEMORY RUNTIME INTEGRATION

Purpose:
Define the bounded runtime hook that allows market_analyzer_v1 live requests
to pass through the external-memory admission path without mutating the
existing analyzer recommendation path.

Runtime Rule:
The external-memory path is parallel, not authoritative.

Existing analyzer output remains primary.
External memory produces:
- qualification record
- qualification receipt
- persistence or rejection receipt
- operator-safe panel

Suggested Live Hook:
After live input has been normalized and runtime classification has been
resolved, call:

run_market_analyzer_external_memory_path(
    request_id=...,
    symbol=...,
    headline=...,
    price_change_pct=...,
    sector=...,
    confirmation=...,
    event_theme=...,
    macro_bias=...,
    route_mode=...,
)

Expected Return:
{
  "artifact_type": "external_memory_runtime_result",
  "status": "ok",
  "qualification_decision": "...",
  "qualification_record": {...},
  "qualification_receipt": {...},
  "persistence_receipt": {...},
  "panel": {...}
}

Integration Rule:
This result may be projected into operator-facing response as:

external_memory_panel

It may not:
- rewrite recommendation logic
- override PM influence
- mutate confidence directly
- suppress existing runtime panels

Recommended Response Placement:
Top-level operator response may include:

external_memory_panel: result["panel"]

Phase 1 Limitation:
This integration supports admission-side memory only.
It does not yet:
- retrieve prior external memory
- promote stored memory into future weighting
- return stored memory into recommendations

That later return path must be built separately.