# EXTERNAL MEMORY PROMOTION POLICY

Purpose:
Define the lawful rules for converting retrieved external-memory records into
promoted reusable memory artifacts.

Required Inputs:
- external_memory_retrieval_artifact
- external_memory_retrieval_receipt

Minimum Input Law:
- artifact and receipt must be paired
- artifact_type must be external_memory_retrieval_artifact
- receipt_type must be external_memory_retrieval_receipt
- returned_count must equal len(records)
- requester_profile must be present
- target_child_core must be present

Phase 3 Promotion Method:
A promotion candidate is scored from the retrieved record set using:

promotion_score =
  average_adjusted_weight
  + average_source_quality_weight
  + coherence_bonus
  - contamination_drag

Definitions:
- average_adjusted_weight:
  mean of retrieved record adjusted_weight values
- average_source_quality_weight:
  mean of retrieved record source_quality_weight values
- coherence_bonus:
  +10 when all records match the same symbol
  +6 when all records match the same sector
  +4 when all records share source_type
  otherwise 0
- contamination_drag:
  mean contamination_penalty across records

Trust Class Rule:
Any retrieved record with trust_class in:
- blocked
- disallowed
- unverifiable

causes immediate promotion rejection.

Phase 3 Thresholds:
PROMOTE_THRESHOLD = 95
HOLD_THRESHOLD = 75

Decisions:
- promotion_score >= PROMOTE_THRESHOLD
  -> promoted
- HOLD_THRESHOLD <= promotion_score < PROMOTE_THRESHOLD
  -> hold
- promotion_score < HOLD_THRESHOLD
  -> reject

Output Requirements:
Promoted artifacts must include:
- target_child_core
- requester_profile
- promoted_records
- promotion_score
- rationale
- bounded advisory summary

Rejection Requirements:
Rejection must include:
- failure reason
- score if available
- record count

Hold Requirements:
Hold is explicit.
Phase 3 does not persist hold as a new durable class.

Phase 3 Limitation:
Promotion is bounded to the current retrieved set.
It does not yet:
- compare across historical retrieval batches
- compute long-horizon recurrence
- alter runtime or PM outputs directly