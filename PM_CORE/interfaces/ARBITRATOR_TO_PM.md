# ARBITRATOR_TO_PM Interface

## Purpose

This interface defines the lawful handoff from REFINEMENT_ARBITRATOR into PM_CORE.

It exists so Stage 16 arbitration decisions can enter PM review without blurring into PM routing authority, PM continuity memory, or child-core execution.

## Upstream Authority

Allowed upstream authority:

- REFINEMENT_ARBITRATOR

Disallowed upstream authority:

- raw RESEARCH_CORE packet
- child-core self-escalation
- direct engine output without arbitration packet
- runtime prompt text

## Accepted Artifact

PM_CORE accepts only an arbitration decision packet emitted by REFINEMENT_ARBITRATOR.

Minimum required fields:

- arbitration_id
- source_packet_id
- issuing_layer
- reasoning_weight
- human_tempering_weight
- child_core_fit_scores
- composite_weight
- recommended_action
- justification_summary
- timestamp

## PM Intake Rule

The arbitration decision packet enters PM through:

AI_GO/PM_CORE/refinement/arbitration_intake.py

This intake surface may:

- validate arbitration packet structure
- create a PM intake record
- create a PM intake receipt
- preserve target child-core recommendation

This intake surface may not:

- activate a child core
- complete PM routing
- mutate RESEARCH_CORE truth
- write PM continuity memory as canonical decision history

## Output Artifact

The PM intake surface emits:

- pm_intake_record
- pm_intake_receipt

These artifacts prepare the packet for later PM refinement and strategic interpretation.

## Decision Meaning Inside PM

PM receives the arbitrator recommendation as upstream propagation guidance, not as binding routing truth.

PM may later use the intake record for:

- refinement review
- strategic interpretation
- inheritance preparation
- child-core routing deliberation

PM does not inherit hidden logic from the arbitrator. The scored basis must remain visible.

## Summary

ARBITRATOR_TO_PM is the governed handoff that allows Stage 16 arbitration results to enter PM review lawfully while preserving the boundary between refinement governance and PM authority.