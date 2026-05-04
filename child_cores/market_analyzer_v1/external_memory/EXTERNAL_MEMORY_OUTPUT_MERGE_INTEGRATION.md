# MARKET ANALYZER EXTERNAL MEMORY OUTPUT MERGE INTEGRATION

Purpose:
Define the bounded merge hook that projects external-memory advisory context
into market_analyzer_v1 operator output safely.

Rule:
Merge is additive and advisory only.

Suggested Merge Call:
merge_market_analyzer_external_memory_output(
    operator_response=response_dict,
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
  "merged_response": {...} | None,
  "receipt": {
    "artifact_type": "external_memory_output_merge_receipt"
    ...
  } | {
    "artifact_type": "external_memory_output_merge_rejection_receipt"
    ...
  }
}

Safe Merge Targets:
- merged_response["external_memory_merge_status"]
- merged_response["external_memory_return_panel"]
- merged_response["external_memory_provenance_refs"]
- merged_response["cognition_panel"]["external_memory_advisory"]

Protected Existing Surfaces:
- recommendation_panel
- governance_panel
- pm_workflow_panel
- execution_allowed
- approval_required
- route_mode

Phase 5 Limitation:
This integration safely projects advisory context into operator output.
It does not:
- alter recommendations
- alter confidence
- alter PM influence
- alter runtime execution state