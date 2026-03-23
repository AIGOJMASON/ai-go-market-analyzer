# PM_CONTINUITY Policy

## Purpose

This policy defines what PM_CONTINUITY is allowed to remember, what it must ignore, and how PM-local continuity should be updated.

Its purpose is to keep Stage 17 bounded and prevent PM continuity from absorbing noise, research truth, or execution authority.

## Core Policy

PM_CONTINUITY remembers PM-relevant decision continuity, not raw information abundance.

That means it should preserve:

- PM intake history
- PM-observed refinement usage
- PM-observed child-core recommendation patterns
- PM unresolved patterns that recur
- PM-local changes that affect future PM decisions

It should not preserve:

- raw screened research as continuity truth
- narrative elaboration for its own sake
- full copies of artifacts when references are sufficient
- child-core runtime state
- system-wide operational memory outside PM scope

## Allowed Inputs

PM_CONTINUITY may update from:

- pm_intake_record
- pm_refinement_record
- strategic_interpretation_record
- governed unresolved PM artifacts if later defined

## Disallowed Inputs

PM_CONTINUITY must reject:

- raw screened research packets
- unscreened external material
- direct child-core runtime state
- arbitrary prompt text as continuity truth
- canon edits
- registry mutation requests

## Recording Rule

PM_CONTINUITY should store references and summaries, not uncontrolled copies.

Preferred practice:

- store source IDs
- store target child-core references
- store recommended action summaries
- store continuity counters
- store timestamps
- store small PM-facing summaries when useful

It should avoid storing large redundant payloads when a reference is enough.

## Change Ledger Rule

A new ledger entry should be written when:

- a new PM intake record is accepted
- a meaningful recommendation shift occurs
- a repeated child-core pattern becomes visible
- an unresolved pattern becomes significant
- PM continuity state changes in a way that matters to future PM review

Not every trivial field update needs a new conceptual ledger entry.

## Unresolved Queue Rule

An unresolved item should enter the PM unresolved queue when:

- PM repeatedly encounters ambiguity not resolved upstream
- multiple child-core fits recur without clear PM resolution
- refinement recommendations repeatedly stall in hold state
- the same downstream question remains materially open across cycles

The unresolved queue is for recurring PM pressure, not every temporary uncertainty.

## Trend Tracking Rule

PM_CONTINUITY may track bounded trends such as:

- which child core is most often recommended
- how often certain recommendations recur
- how often PM receives hold vs pass_to_pm vs condition_for_child_core
- how often certain unresolved categories recur

Trend tracking must remain lightweight and operational.

## Non-Authority Rule

PM_CONTINUITY may inform PM, but it may not decide in place of PM.

It must not:

- auto-route work
- auto-activate child cores
- reclassify research truth
- issue execution commands
- promote itself to governance over PM

## Entropy Rule

Continuity should remain compressed.

If PM continuity starts accumulating low-value repetition, it should:

- summarize instead of duplicate
- increment counters instead of storing repeated payloads
- move repeated unresolved items into pattern-based entries
- refuse to preserve noise merely because it exists

## Summary

PM_CONTINUITY remembers only what PM needs to stay coherent across decisions and nothing more.