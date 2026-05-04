# PM_TO_CONTINUITY Interface

## Purpose

This interface defines the lawful handoff from PM-side intake and review surfaces into PM_CONTINUITY.

It exists so PM continuity updates occur through explicit governed artifacts rather than implicit memory accumulation.

## Upstream Authority

Allowed upstream authorities:

- pm.refinement.arbitration_intake
- PM refinement surfaces
- strategic interpretation surfaces

Disallowed upstream authorities:

- RESEARCH_CORE direct packet flow
- REFINEMENT_ARBITRATOR direct continuity mutation
- child-core runtime
- raw prompt text

## Accepted Artifact Types

PM_CONTINUITY may accept:

- pm_intake_record
- pm_refinement_record
- strategic_interpretation_record

This initial Stage 17 build requires at minimum support for pm_intake_record.

## PM Continuity Intake Rule

A PM continuity intake surface may:

- validate the incoming PM artifact
- create or update PM continuity state
- write a PM change ledger entry when warranted
- create or update a PM unresolved queue record when warranted
- emit a continuity receipt

It may not:

- change PM routing truth
- activate child cores
- rewrite upstream research or arbitrator truth
- mutate canon directly

## Minimum PM Intake Fields

At minimum, PM continuity requires fields such as:

- source PM artifact ID
- source packet or arbitration reference
- recommended action
- target child core if any
- timestamp
- PM status summary

## Output Artifacts

PM_CONTINUITY may emit:

- pm_continuity_update
- pm_continuity_receipt

It may also update:

- pm_continuity_state
- pm_change_ledger
- pm_unresolved_queue

## Summary

PM_TO_CONTINUITY is the governed PM-side handoff that allows PM decision-memory state to update from PM-local artifacts without collapsing into routing, execution, or system-wide memory authority.