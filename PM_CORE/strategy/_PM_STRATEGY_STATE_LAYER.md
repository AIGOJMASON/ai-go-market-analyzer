# PM_STRATEGY State Layer

## Purpose

This state layer defines the live, non-canon persistence surfaces for Stage 18 PM_STRATEGY activity.

It exists to preserve current PM strategic-decision state, decision ledger state, and receipt references required for PM strategy operation without confusing live state with canon truth.

## State Role

PM strategy state is operational, not canonical.

It may store:

- current PM strategic decision state
- PM decision ledger state
- recent decision packet references
- recent strategy receipt references

It may not store:

- child-core activation truth as independent authority
- runtime routing truth as final archive
- research truth rewrites
- canon history as though state were archive
- system-wide operational memory outside PM strategy scope

## Canonical State Structure

AI_GO/
  PM_CORE/
    strategy/
      _PM_STRATEGY_STATE_LAYER.md
  PM_CORE/
    state/
      current/
        pm_strategy_state.json
        pm_decision_ledger.json

## Current Strategy State Surface

The current strategy state surface exists for live PM decision visibility.

It should track:

- total PM decisions
- recent decision packet IDs
- decision counts by action
- decision counts by core
- last updated timestamp

This file is live operational state, not archive authority.

## Decision Ledger Surface

The decision ledger surface exists for persisted PM strategic decision entries.

It should store:

- decision packet IDs
- source continuity references
- recommended action summaries
- target child-core recommendations
- timestamps

It provides durable PM-local strategic history while remaining separate from canon.

## Update Rule

PM strategy state must update only through governed Stage 18 execution paths.

Permitted update sources:

- PM_CONTINUITY update outputs
- PM strategy execution
- future PM strategic receipt linkage if separately defined

PM strategy state must not be mutated by:

- raw screened research packets
- REFINEMENT_ARBITRATOR direct mutation
- child-core runtime
- user prompt text
- canon registry processes

## Separation Rule

This layer is intentionally separate from:

- lib/ archive truth
- runtime router receipts
- RESEARCH_CORE state
- child-core state
- PM continuity state

Its scope is PM strategic decision state only.

## One-Line Definition

The PM_STRATEGY state layer is the live operational persistence surface for Stage 18 strategic decisions and decision-ledger state, kept structurally separate from canon, execution authority, and routing truth.