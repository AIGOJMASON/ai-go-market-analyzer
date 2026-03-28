# EXTERNAL MEMORY PATTERN AGGREGATION POLICY

## Purpose

Formalize the lawful conversion of promoted external-memory records into bounded pattern-aggregation artifacts.

## Accepted Inputs

### Promotion Artifact

Required top-level fields:

- artifact_type
- target_core
- requester_profile
- promotion_status
- promoted_records
- promoted_record_count
- provenance_refs

Expected artifact_type:

- external_memory_promotion

Expected promotion_status:

- promoted

### Promotion Receipt

Required fields:

- receipt_type
- artifact_type
- target_core
- requester_profile
- status

Expected receipt_type:

- external_memory_promotion_receipt

Expected status:

- success

## Allowed Requester Profiles

- operator
- analyzer
- pm

## Allowed Target Cores

Initial bounded target list:

- market_analyzer_v1

## Required Record Fields

Each promoted record must include:

- memory_id
- symbol
- sector
- event_theme
- source_quality
- trust_class
- adjusted_weight
- observed_at

Optional bounded record fields:

- source_ref
- source_type
- headline
- pattern_key

## Aggregation Rules

### 1. Recurrence Count

Recurrence count equals the number of promoted records in the artifact.

### 2. Dominant Symbol

The dominant symbol is the most frequent non-empty symbol across promoted records.
Ties resolve to the symbol associated with the highest summed adjusted_weight.

### 3. Dominant Sector

The dominant sector is the most frequent non-empty sector across promoted records.
Ties resolve to the sector associated with the highest summed adjusted_weight.

### 4. Temporal Span

Temporal span is the difference in days between earliest and latest observed_at timestamps.
If only one record exists, span is 0.

### 5. Recency Weight

Recency weight is bounded in the interval [0.20, 1.00].

Suggested deterministic model:

- span <= 2 days => 1.00
- span <= 7 days => 0.85
- span <= 14 days => 0.70
- span <= 30 days => 0.50
- span > 30 days => 0.20

### 6. Base Pattern Score

Base pattern score =
(
  normalized recurrence strength * 0.45
  +
  normalized adjusted-weight mean * 0.35
  +
  recency weight * 0.20
)

Where:

- normalized recurrence strength = min(recurrence_count / 5.0, 1.0)
- normalized adjusted-weight mean = min(mean(adjusted_weight) / 100.0, 1.0)

### 7. Pattern Strength

Thresholds:

- score < 0.35 => weak_pattern
- score < 0.60 => forming_pattern
- score < 0.82 => strong_pattern
- score >= 0.82 => dominant_pattern

### 8. Pattern Posture

Mapping:

- weak_pattern => light_pattern_context
- forming_pattern => useful_pattern_context
- strong_pattern => strong_pattern_context
- dominant_pattern => strong_pattern_context

### 9. Historical Confirmation

Mapping:

- recurrence_count <= 1 => low_confirmation
- recurrence_count <= 3 => moderate_confirmation
- recurrence_count >= 4 => high_confirmation

### 10. Pattern Summary

Pattern summary is bounded human-readable text containing:

- recurrence count
- dominant symbol or sector
- temporal span
- pattern strength
- historical confirmation

The summary may not add claims not present in the artifact.

## Output Artifact Requirements

The output artifact must include:

- artifact_type
- source_artifact_type
- target_core
- requester_profile
- recurrence_count
- temporal_span_days
- recency_weight
- dominant_symbol
- dominant_sector
- pattern_strength
- pattern_posture
- historical_confirmation
- promoted_record_count
- promoted_memory_ids
- pattern_summary
- provenance_refs
- aggregation_score
- aggregation_status

Expected output artifact_type:

- external_memory_pattern_aggregation

Expected aggregation_status:

- aggregated

## Receipt Requirements

Success receipt must include:

- receipt_type
- artifact_type
- status
- target_core
- requester_profile
- recurrence_count
- pattern_strength
- historical_confirmation

Expected receipt_type:

- external_memory_pattern_aggregation_receipt

Rejection receipt must include:

- receipt_type
- artifact_type
- status
- failure_reason
- target_core
- requester_profile

Expected rejection receipt_type:

- external_memory_pattern_aggregation_rejection_receipt

## Hard Constraints

- no hidden weighting fields
- no direct runtime influence
- no recommendation mutation
- no persistence writes
- no raw-record leakage beyond bounded promoted lineage
- no consumer shaping beyond the pattern artifact itself

## Next Layer

Successful pattern aggregation may be consumed by return path.
Return path remains the authority that converts pattern artifacts into advisory packet form.