Next is Stage 16 closeout: state-layer definition, arbitration index, registry updates, final # REFINEMENT_ARBITRATOR State Layer

## Purpose

This state layer defines the live, non-canon persistence surface for Stage 16 REFINEMENT_ARBITRATOR activity.

It exists to preserve current arbitration outputs, receipts, and indexing truth needed for runtime continuity without confusing live state with canon authority.

## State Role

REFINEMENT_ARBITRATOR state is operational, not canonical.

It may store:

- current arbitration decision artifacts
- current arbitration receipts
- live arbitration index records
- bounded references to PM intake receipt linkage

It may not store:

- PM continuity authority
- child-core activation truth
- research truth rewrites
- final strategic routing decisions
- canon history as though state were archive

## Allowed State Partitions

Canonical state structure:

AI_GO/
  state/
    refinement_arbitrator/
      _REFINEMENT_ARBITRATOR_STATE_LAYER.md
      current/
        arbitration_index.json
      receipts/

## Current State Surface

The current surface exists for live arbitration visibility.

It should track:

- active arbitration IDs
- linked source packet IDs
- recommended actions
- target child-core recommendations
- decision artifact paths
- arbitration receipt paths
- PM intake receipt refs when available
- last updated timestamp

This is a live operational index, not a historical archive ledger.

## Receipt Surface

The receipts surface exists for persisted arbitration receipts.

It should store:

- arbitration receipt artifacts
- receipt-bearing visibility records for Stage 16 decisions

Receipt persistence is required so propagation cost remains inspectable.

## State Update Rule

State must only update through governed Stage 16 execution paths.

Permitted update sources:

- REFINEMENT_ARBITRATOR engine output
- PM arbitration intake receipt linkage when explicitly recorded as a reference

State must not be mutated by:

- raw user prompt
- unscreened research material
- child-core runtime
- PM continuity layer
- canon registry processes

## Separation Rule

This layer is intentionally separate from:

- lib/ archive and canon truth
- PM continuity memory
- child-core state
- RESEARCH_CORE state

Its job is narrow:
retain live arbitration visibility long enough for bounded runtime inspection and lawful handoff.

## Lifecycle Rule

State entries may persist while operationally relevant.

When no longer current, they should:

- be replaced in the current index
- remain represented through receipts
- or be archived through a future governed lifecycle process if such a process is later defined

No state entry gains canon authority merely by persisting.

## Minimum Index Fields

The arbitration index should maintain records using fields such as:

- arbitration_id
- source_packet_id
- recommended_action
- target_child_core
- decision_path
- receipt_path
- pm_intake_receipt_path
- timestamp
- status

## One-Line Definition

The REFINEMENT_ARBITRATOR state layer is the live operational persistence surface for Stage 16 arbitration outputs and receipts, kept structurally separate from canon, PM continuity, and execution authority.