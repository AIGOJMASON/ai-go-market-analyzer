# EXTERNAL MEMORY QUALIFICATION POLICY

Purpose:
Define the lawful pre-DB decision rules for whether a governed external
record deserves durable persistence.

Primary Question:
Does this record deserve storage cost?

This is different from:
- may this be analyzed?
- may this be interpreted?
- may this be routed?

Those questions are upstream.

This layer answers only:
- may this persist?

Required Inputs:
A lawful qualification request must include:
- artifact_type
- source_type
- source_quality_weight
- signal_quality_weight
- domain_relevance_weight
- persistence_value_weight
- contamination_penalty
- redundancy_penalty
- trust_class
- payload
- target_child_cores
- provenance

Minimum Input Law:
Missing required fields produce rejection.
Ungoverned payloads produce rejection.
Implicit defaults are forbidden for source quality and trust class.

Decision Method:
The engine computes:
base_weight =
  source_quality_weight
  + signal_quality_weight
  + domain_relevance_weight
  + persistence_value_weight

adjusted_weight =
  base_weight
  - contamination_penalty
  - redundancy_penalty

Hard Floors:
1. source_quality_weight must be >= SOURCE_QUALITY_FLOOR
2. trust_class must not be in BLOCKED_TRUST_CLASSES

Decision Thresholds:
- adjusted_weight >= PERSIST_THRESHOLD
  -> persist_candidate
- HOLD_THRESHOLD <= adjusted_weight < PERSIST_THRESHOLD
  -> hold
- adjusted_weight < HOLD_THRESHOLD
  -> reject

Phase 1 Policy Constants:
SOURCE_QUALITY_FLOOR = 25
PERSIST_THRESHOLD = 70
HOLD_THRESHOLD = 50

Blocked Trust Classes:
- blocked
- disallowed
- unverifiable

Design Notes:
- A signal can be lawful to inspect and still unlawful to persist.
- Source quality is a primary weight and a hard floor.
- Hold exists to preserve semantic distinction but does not write to DB in Phase 1.
- Rejection is explicit, not silent.

Outputs:
- external_memory_qualification_record
- external_memory_qualification_receipt

Disallowed Behaviors:
- no direct DB write from qualification
- no PM strategy mutation
- no runtime mutation
- no SMI write
- no auto-promotion to training memory