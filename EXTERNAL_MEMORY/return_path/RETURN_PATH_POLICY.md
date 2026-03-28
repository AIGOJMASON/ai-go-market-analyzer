# EXTERNAL MEMORY RETURN PATH POLICY

## Purpose

Formalize the lawful conversion of external-memory context into bounded advisory return packets.

This stage now accepts either:

- promoted memory artifacts
- pattern-aggregation artifacts

Return path remains advisory only.

## Accepted Inputs

### Accepted Artifact Types

- external_memory_promotion
- external_memory_pattern_aggregation

### Accepted Receipt Types

When artifact_type = external_memory_promotion:

- external_memory_promotion_receipt

When artifact_type = external_memory_pattern_aggregation:

- external_memory_pattern_aggregation_receipt

## Required Common Inputs

Artifact required fields:

- artifact_type
- target_core
- requester_profile
- provenance_refs

Receipt required fields:

- receipt_type
- artifact_type
- target_core
- requester_profile
- status

## Pattern-Aggregation Specific Requirements

If artifact_type = external_memory_pattern_aggregation, the artifact must also contain:

- aggregation_status
- recurrence_count
- temporal_span_days
- recency_weight
- dominant_symbol
- dominant_sector
- pattern_strength
- pattern_posture
- historical_confirmation
- pattern_summary
- promoted_memory_ids

Expected aggregation_status:

- aggregated

## Promotion Specific Requirements

If artifact_type = external_memory_promotion, the artifact must also contain:

- promotion_status
- promoted_record_count
- promoted_records

Expected promotion_status:

- promoted

## Allowed Requester Profiles

- operator
- analyzer
- pm

## Allowed Target Cores

- market_analyzer_v1

## Advisory Posture Rules

### From Promotion

- promoted_record_count >= 3 => strong_context
- promoted_record_count == 2 => useful_context
- promoted_record_count == 1 => light_context

### From Pattern Aggregation

- pattern_posture = strong_pattern_context => strong_context
- pattern_posture = useful_pattern_context => useful_context
- pattern_posture = light_pattern_context => light_context

## Return Packet Requirements

The emitted advisory return packet must include:

- artifact_type
- target_core
- requester_profile
- advisory_posture
- external_memory_return_panel
- external_memory_provenance_refs

Expected output artifact_type:

- external_memory_return_packet

## Pattern Context Panel Rules

If source artifact is pattern aggregation, the return panel must include:

- recurrence_count
- temporal_span_days
- dominant_symbol
- dominant_sector
- pattern_strength
- historical_confirmation
- pattern_summary

## Promotion Context Panel Rules

If source artifact is promotion, the return panel must include:

- promoted_record_count
- promoted_memory_ids
- summary posture fields only

## Rejection Vocabulary

- invalid_return_source_artifact_type
- invalid_return_source_receipt_type
- artifact_receipt_misalignment
- target_not_allowed
- requester_profile_not_allowed
- source_status_not_accepted
- missing_required_fields
- invalid_source_shape

## Hard Constraints

- no runtime mutation
- no PM mutation
- no recommendation mutation
- no governance-panel mutation
- no raw retrieval leakage
- no advisory packet without valid source artifact and receipt pairing

## Next Layer

Output merge remains the next lawful stage.