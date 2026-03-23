# PM State Layer

## Purpose

This state layer defines the live, non-canon persistence surfaces owned by PM_CORE.

It exists to preserve current PM-local records, continuity state, change-ledger state, unresolved state, and receipt-bearing references required for PM operation without confusing live state with canon truth.

## State Role

PM state is operational, not canonical.

It may store:

- PM continuity state
- PM change ledger state
- PM unresolved queue state
- PM intake receipt references
- bounded PM-local current operational records

It may not store:

- archive truth as though state were canon
- child-core activation truth as independent authority
- research truth rewrites
- runtime routing truth as final archive
- system-wide memory outside PM scope

## Canonical State Structure

AI_GO/
  PM_CORE/
    state/
      _PM_STATE_LAYER.md
      current/
        pm_continuity_state.json
        pm_change_ledger.json
        pm_unresolved_queue.json
      receipts/

## Current State Surface

The current PM state surface exists for live PM continuity and review support.

It should store:

- current PM continuity counters
- recent PM intake references
- recent source arbitration references
- current change ledger entries
- current unresolved PM patterns
- last updated timestamps

These files are live operational state, not archive authority.

## Receipts Surface

The receipts surface exists for persisted PM-facing receipts and references.

It may contain:

- PM intake receipts
- future PM continuity receipts if separately persisted
- bounded PM receipt visibility artifacts

## Update Rule

PM state must update only through governed PM execution surfaces.

Permitted update sources include:

- PM arbitration intake
- PM continuity update surface
- future PM refinement and strategic surfaces if later governed

PM state must not update from:

- raw screened research packets
- REFINEMENT_ARBITRATOR direct mutation
- child-core runtime direct writes
- user prompt text
- canon registry processes

## Separation Rule

This state layer is intentionally separate from:

- lib/ archive truth
- runtime router receipts
- RESEARCH_CORE state
- child-core state
- system-wide continuity

Its scope is PM-owned live state only.

## Lifecycle Rule

PM state persists while operationally relevant.

When entries become stale or superseded, they may be:

- summarized
- replaced in current state
- retained in bounded ledger form
- or moved through a future governed lifecycle process if later defined

No PM state file becomes canon merely by existing.

## One-Line Definition

The PM state layer is the live operational persistence surface for PM continuity, PM change history, and PM unresolved review state, kept structurally separate from archive truth and execution authority.