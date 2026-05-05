# MARKET ANALYZER V1 EXTERNAL MEMORY PATTERN AGGREGATION INTEGRATION

## Purpose

Document how market_analyzer_v1 may consume promoted external-memory outputs and convert them into bounded pattern-aggregation artifacts before return path.

## Entry Point

- AI_GO/child_cores/market_analyzer_v1/external_memory/pattern_aggregation.py

## Upstream Dependency

This adapter accepts only:

- external_memory_promotion artifact
- external_memory_promotion_receipt

The upstream promotion layer must have already decided that the retrieved memory batch is promotable.

## Emitted Output

On success, the adapter returns:

- external_memory_pattern_aggregation artifact
- external_memory_pattern_aggregation_receipt

On failure, the adapter returns:

- external_memory_pattern_aggregation_rejection_receipt

## What This Layer Adds

This layer adds:

- recurrence_count
- temporal_span_days
- recency_weight
- dominant_symbol
- dominant_sector
- pattern_strength
- pattern_posture
- historical_confirmation
- pattern_summary

## What This Layer Does Not Add

This layer does not:

- mutate promoted records
- write to persistence
- shape operator output
- alter recommendations
- alter governance panels
- replace return path

## Next Lawful Consumer

The next lawful consumer is the external-memory return path.

Return path remains the authority that converts this aggregated pattern context into an advisory packet for operator-facing use.

## Integration Rule

Market analyzer may call this layer only after promotion succeeds and before return path is invoked.

The canonical chain becomes:

promotion
→ pattern aggregation
→ return path
→ output merge

## Hard Boundary

Pattern aggregation remains advisory-only and non-authoritative.

It may strengthen visible context.
It may not change recommendation logic.