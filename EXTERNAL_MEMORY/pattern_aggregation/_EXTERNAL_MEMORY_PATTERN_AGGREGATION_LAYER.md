# EXTERNAL MEMORY PATTERN AGGREGATION LAYER

## Purpose

Define the bounded external-memory pattern-aggregation authority.

This layer sits after promotion and before return path.

It converts promoted external-memory records into a sealed pattern-aggregation artifact that can express recurrence, temporal weighting, and pattern-strength posture without mutating runtime, PM, recommendation logic, or committed memory truth.

## Stage Scope

Stage 67 for the external-memory system.

This stage is not raw memory expansion.
It is governed pattern formation over already promoted memory.

## Input

- promoted external-memory artifact
- matched promotion receipt

## Output

- external_memory_pattern_aggregation artifact
- pattern-aggregation receipt
- bounded rejection receipt

## Hard Rules

1. Pattern aggregation may only consume promoted memory outputs.
2. Pattern aggregation is advisory only.
3. Pattern aggregation may not write back into persistence.
4. Pattern aggregation may not mutate promotion truth.
5. Pattern aggregation may not alter recommendation logic.
6. Pattern aggregation must expose visible weighting and recurrence fields.
7. Pattern aggregation must preserve source lineage and provenance references.
8. Pattern aggregation must remain target-bounded by child core.

## Non-Responsibilities

This layer does not:

- ingest raw external signals
- persist new memory records
- perform retrieval
- replace promotion
- perform return-path shaping
- merge into operator output
- mutate PM, watcher, or runtime state

## Why This Layer Exists

Promotion answers:

"What retrieved memory matters now?"

Pattern aggregation answers:

"What repeated promoted memory forms a bounded pattern over time?"

Without this layer, the system can surface only promoted batch meaning.
With this layer, the system can lawfully surface recurrence, strengthening, and historical confirmation while preserving authority boundaries.

## Core Outputs

The emitted pattern artifact must contain:

- target_core
- requester_profile
- promoted_record_count
- recurrence_count
- temporal_span_days
- recency_weight
- dominant_symbol
- dominant_sector
- pattern_strength
- pattern_posture
- historical_confirmation
- provenance_refs
- pattern_summary

## Pattern Strength Vocabulary

- weak_pattern
- forming_pattern
- strong_pattern
- dominant_pattern

## Pattern Posture Vocabulary

- light_pattern_context
- useful_pattern_context
- strong_pattern_context

## Historical Confirmation Vocabulary

- low_confirmation
- moderate_confirmation
- high_confirmation

## Rejection Vocabulary

- invalid_promotion_artifact_type
- invalid_promotion_receipt_type
- artifact_receipt_misalignment
- target_not_allowed
- requester_profile_not_allowed
- promotion_status_not_promoted
- empty_promoted_records
- missing_required_fields
- invalid_record_shape

## Where It Connects

- PATTERN_AGGREGATION_POLICY.md
- pattern_aggregation_registry.py
- pattern_aggregation_runtime.py
- pattern_aggregation_receipt_builder.py
- child-core pattern adapters
- return-path runtime as the next advisory shaping layer