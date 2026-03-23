# PM_STRATEGY Policy

## Purpose

Defines how PM_STRATEGY consolidates inputs into decisions.

## Core Rule

PM decisions must be:

- bounded
- reference-based
- continuity-aware
- non-authoritative over execution

## Decision Construction

PM_STRATEGY should:

- prioritize recent continuity signals
- observe action frequency trends
- consider unresolved pressure
- favor stable patterns over single events

## Decision Output Requirements

Each decision packet must include:

- source continuity references
- decision intent
- recommended action
- target child core (if applicable)
- reasoning summary (compressed)
- timestamp

## Disallowed Behavior

PM_STRATEGY must not:

- fabricate inputs
- directly execute outcomes
- rewrite upstream artifacts
- expand beyond PM scope

## Entropy Rule

Prefer:

- summarized reasoning
- reference IDs over duplication
- trend indicators over raw repetition

## One-Line Rule

PM_STRATEGY decides using memory, not noise.