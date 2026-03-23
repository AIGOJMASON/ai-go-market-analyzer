# PM_STRATEGY Layer

## Purpose

PM_STRATEGY is the Stage 18 consolidation layer for PM_CORE.

It exists to transform PM continuity, refinement outputs, and strategic interpretation into a bounded, governed decision packet for downstream routing.

This layer is where PM forms its position.

## Why This Layer Exists

After Stage 16 (REFINEMENT_ARBITRATOR) and Stage 17 (PM_CONTINUITY):

- signals are governed
- PM has memory

Stage 18 is required so PM can **decide coherently using that memory**.

Without this layer:

- PM continuity remains passive
- refinement outputs remain unstructured
- downstream routing lacks a unified PM decision artifact

## Core Function

PM_STRATEGY:

- consumes PM_CONTINUITY updates
- consumes PM refinement and interpretation outputs
- consolidates signals into a structured PM decision
- emits a `pm_decision_packet`

## Authority Boundary

PM_STRATEGY may:

- consolidate PM-side inputs
- interpret continuity trends
- produce decision packets
- recommend child-core targets
- express PM-level intent

PM_STRATEGY may not:

- rescore research packets
- override REFINEMENT_ARBITRATOR
- mutate PM continuity directly
- activate child cores
- execute routing
- mutate canon truth

## Inputs

- pm_continuity_update
- pm_refinement_record (future)
- strategic_interpretation_record (future)

## Outputs

- pm_decision_packet
- pm_strategy_receipt

## Stage Identity

Stage 18 = PM strategic decision consolidation

## One-Line Definition

PM_STRATEGY is the PM decision layer that converts continuity and refinement into a governed downstream decision packet.