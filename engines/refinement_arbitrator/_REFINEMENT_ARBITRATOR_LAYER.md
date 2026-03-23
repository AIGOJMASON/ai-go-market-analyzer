# REFINEMENT_ARBITRATOR Layer

## Purpose

REFINEMENT_ARBITRATOR is the Stage 16 upstream refinement-governance layer for AI_GO.

It exists to evaluate screened, trusted RESEARCH_CORE output before unnecessary downstream propagation occurs. Its purpose is not to create truth, route execution, or store PM memory. Its purpose is to govern whether a research signal deserves deeper refinement, child-core conditioning, PM exposure, or discard.

This layer is the first formal propagation-control surface in the architecture.

## Core Function

REFINEMENT_ARBITRATOR receives a governed research packet that has already passed RESEARCH_CORE intake, screening, and trust classification.

It then determines whether that packet should be:

- discarded
- held
- conditioned for one or more child cores
- sent to Curved Mirror for reasoning refinement
- sent to Rosetta for narrative refinement
- passed forward to PM_CORE as sufficient

The arbitrator does not decide strategic execution. It decides refinement worth and downstream propagation fitness.

## Why This Layer Exists

Without REFINEMENT_ARBITRATOR, PM_CORE would absorb too much filtering pressure internally.

That would cause:

- PM overload
- noisy signal propagation
- over-refinement
- weak child-core conditioning
- architecture blur between research, refinement, and routing
- persistence of low-value signal without entropic payment

This layer prevents that failure mode by forcing signal evaluation before PM absorbs it.

## Authority Boundary

REFINEMENT_ARBITRATOR is a refinement-governance layer only.

It may:

- evaluate packet value
- compute reasoning-weight and human-tempering contribution
- compute child-core fit scores
- compute composite downstream propagation scores
- emit bounded recommendations
- issue arbitration receipts

It may not:

- create or alter research truth
- mutate RESEARCH_CORE trust state
- mutate PM routing state
- activate child cores
- write PM continuity memory as authoritative history
- bypass PM and send execution work directly into child-core runtime
- rewrite canon truth
- become a hidden decision-maker outside its receipt surface

## Placement

This layer sits in the engines family because it is a refinement-governance surface and belongs alongside Curved Mirror and Rosetta.

Canonical location:

AI_GO/
  engines/
    refinement_arbitrator/

This placement preserves the distinction between:

- upstream refinement triage
- PM strategic decision authority
- later PM continuity memory

## Upstream Dependencies

REFINEMENT_ARBITRATOR depends on:

- RESEARCH_CORE screened packet outputs
- Curved Mirror reasoning refinement surfaces when invoked
- Rosetta narrative refinement surfaces when invoked
- child-core profile definitions
- bounded scoring and decision policy

It does not depend on PM continuity state to function.

## Downstream Relationship

The arbitrator emits a decision artifact that PM_CORE may consume.

That artifact may recommend:

- discard
- hold
- condition_for_child_core
- send_to_curved_mirror
- send_to_rosetta
- pass_to_pm

PM_CORE remains the authority for routing, inheritance, and execution decisions.

REFINEMENT_ARBITRATOR does not replace PM. It sharpens what reaches PM.

## Entropy Rule

A research packet may not propagate downstream solely because it exists.

It must earn downstream propagation through scored usefulness under constraint.

In practical terms:

- weak signal should decay or be discarded
- ambiguous signal may be held
- structurally useful signal may be refined
- sufficiently strong signal may pass to PM
- child-core conditioning must be justified, not inferred casually

This makes REFINEMENT_ARBITRATOR the Stage 16 entropic payment layer for research propagation.

## Engine Ordering Rule

Default refinement order is:

1. Curved Mirror first for structural reasoning weight
2. Rosetta second for human-facing tempering weight

This order is mandatory unless explicitly overridden by a future governed policy.

Reasoning must be estimated before presentation is shaped.

## Child-Core Conditioning Rule

No global score is sufficient by itself.

Each child core may require different weighting emphasis.

Examples:

- contractor_proposals_core may privilege structural utility and repeatable signal strength
- louisville_gis_core may privilege domain specificity and reasoning precision
- future narrative or education-oriented cores may privilege Rosetta tempering more heavily

Therefore arbitrator decisions must be profile-aware, not globally uniform.

## Required Outputs

This layer must emit:

- arbitration_decision
- reasoning_weight
- human_tempering_weight
- child_core_fit_scores
- composite_weight
- recommended_action
- justification_summary
- arbitration_receipt

## Stage Identity

Stage 16 is the activation of REFINEMENT_ARBITRATOR.

This stage is complete only when the system has:

- a defined arbitrator layer
- bounded input and output contracts
- explicit weighting rules
- child-core-aware fit logic
- explicit decision thresholds
- receipt-bearing decisions that do not blur into PM or child-core execution

## One-Line Definition

REFINEMENT_ARBITRATOR is the governed propagation-control layer that converts screened research into child-core-aware refinement recommendations before PM absorbs downstream signal.