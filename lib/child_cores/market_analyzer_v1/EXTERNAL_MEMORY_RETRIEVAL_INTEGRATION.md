# MARKET ANALYZER EXTERNAL MEMORY RETRIEVAL INTEGRATION

Purpose:
Define the bounded retrieval hook that allows market_analyzer_v1 to read
persisted external-memory records without promoting them, mutating runtime,
or bypassing later promotion logic.

Runtime Rule:
Retrieval is advisory and read-only.

Suggested Retrieval Call:
run_market_analyzer_external_memory_retrieval(
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
    "artifact_type": "external_memory_retrieval_artifact",
    "request_summary": {...},
    "matched_count": ...,
    "returned_count": ...,
    "records": [...]
  } | None,
  "receipt": {
    "artifact_type": "external_memory_retrieval_receipt"
    ...
  } | {
    "artifact_type": "external_memory_retrieval_failure_receipt"
    ...
  }
}

Phase 2 Limitation:
Retrieved records are inspection-ready only.
They do not yet:
- alter recommendation logic
- alter PM influence
- create runtime weighting changes
- become promoted reusable memory

That later behavior belongs to promotion and return-path integration.