# REFINEMENT ARBITRATOR LAYER

## Purpose

The refinement arbitrator layer defines the lawful runtime boundary that converts sealed, already-governed evidence into one bounded `refinement_packet` for operator-facing use.

This layer reintroduces Curved Mirror and Rosetta as constrained refinement consumers under a governed arbitration surface.

## Position in Runtime


accepted + quarantined closeouts + historical analogs
↓
refinement_arbitrator
↓
refinement_packet
↓
refinement_panel (dashboard only)


The runtime decision path remains fully separate and immutable.

## Allowed Responsibilities

- Analyze sealed artifacts only
- Compare accepted vs quarantined outcomes
- Evaluate analog alignment
- Classify refinement posture:
  - supportive
  - neutral
  - cautionary
  - suppressed
- Emit bounded refinement packet

## Forbidden Responsibilities

- Modify candidate selection
- Modify recommendation generation
- Modify execution behavior
- Alter watcher validation
- Alter closeout state
- Inject unbounded reasoning
- Perform hidden learning

## Invariants


execution_influence = false
recommendation_mutation_allowed = false


These must never change.

## Output Contract

Produces:

- `refinement_packet` (sealed)
- Dashboard-compatible refinement panel

## Integration Rule

This layer attaches ONLY to:

- closed artifacts (post-watcher, post-closeout)
- dashboard rendering path

It must not connect upstream into decision logic.

## Summary

This layer enables controlled intelligence:

- deterministic system remains intact
- refinement is visible but non-authoritative
- operator gains context without system risk