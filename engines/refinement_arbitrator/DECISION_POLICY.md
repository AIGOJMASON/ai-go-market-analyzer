
---

# `AI_GO/engines/refinement_arbitrator/DECISION_POLICY.md`

```md
# REFINEMENT_ARBITRATOR Decision Policy

## Purpose

This document defines the bounded actions REFINEMENT_ARBITRATOR may recommend and the conditions under which each recommendation should be used.

The goal is to make arbitration decisions lawful, explainable, and stable.

## Allowed Decisions

REFINEMENT_ARBITRATOR may recommend only the following actions:

- discard
- hold
- condition_for_child_core
- send_to_curved_mirror
- send_to_rosetta
- pass_to_pm

No other decision labels are valid unless canon is updated.

## Decision Definitions

### discard

Use discard when the packet does not justify continued downstream cost.

Conditions commonly include:

- low composite weight
- low reasoning value
- low fit to any active child core
- poor specificity
- high contamination risk without compensating utility
- weak or generic downstream usefulness

Discard means propagation stops here.

### hold

Use hold when the packet is not worthless but not yet fit for propagation.

Conditions commonly include:

- moderate ambiguity
- incomplete scoring inputs
- uncertain child-core fit
- temporary lack of refinement justification
- unresolved relevance under current entropy pressure

Hold means defer, not reject.

### condition_for_child_core

Use this when the packet has enough value to be shaped toward a specific child core, but should not yet go directly to PM as a generally ready packet.

Conditions commonly include:

- moderate-to-strong fit for one child core
- useful signal requiring target-specific framing
- nonzero contamination risk that can be reduced through conditioning
- sufficient structural value, but still too raw for general PM treatment

### send_to_curved_mirror

Use this when structural reasoning weight is insufficiently known or too weak for a stable decision.

Conditions commonly include:

- packet domain relevance is unclear
- reasoning coherence needs testing
- evidence alignment is not sufficiently scored
- core fit might be promising, but structure is underdetermined

This recommendation exists to obtain a structural worth estimate before downstream propagation.

### send_to_rosetta

Use this when structural value is present, but human-facing interpretability or communicative shaping is insufficient for the likely downstream consumer.

Conditions commonly include:

- good reasoning score
- reasonable core fit
- weak clarity or presentation value
- likely benefit from human-facing transformation or tempering

This recommendation exists to improve communicative usability without altering authority truth.

### pass_to_pm

Use this when the packet has already earned downstream propagation into PM.

Conditions commonly include:

- strong or high composite weight
- adequate scoring completeness
- acceptable contamination risk
- no missing critical refinement dimension
- sufficient readiness for PM strategic decision-making

Pass_to_pm means the arbitrator has paid the refinement-governance cost and recommends PM review.

## Threshold Use

Default thresholds should follow the weighting model unless stricter policy is active.

Recommended default mapping:

- 0.00 to 0.29 = discard
- 0.30 to 0.49 = hold
- 0.50 to 0.64 = condition_for_child_core
- 0.65 to 0.79 = send_to_engine_or_pass_to_pm_based_on_gap
- 0.80 to 1.00 = pass_to_pm

Thresholds must not be treated mechanically if a missing score or severe contamination risk exists.

## Gap-Based Override Rule

A threshold result may be overridden by a missing critical dimension.

Examples:

If composite score is moderate-high but reasoning weight is not actually validated:
- send_to_curved_mirror

If composite score is moderate-high but clarity is insufficient for downstream use:
- send_to_rosetta

If composite score is moderate but target-core alignment is high:
- condition_for_child_core

## Entropy-Conservative Rule

When entropy is high and grace is low:

- prefer discard over weak hold accumulation
- prefer hold over speculative pass_to_pm
- do not over-condition weak packets
- do not invoke both engines unless clearly justified
- reduce propagation velocity

## Contamination Rule

If contamination risk is high enough to threaten wrong-core propagation, the arbitrator should not pass the packet downstream merely because one component score is strong.

Permitted responses:

- discard
- hold
- condition_for_child_core with penalty applied

## Multi-Core Fit Rule

A packet may score against more than one child core.

In that case the arbitrator should:

- identify the highest fit core
- note competing fit cores if meaningful
- avoid pretending fit is singular when it is not
- still emit one primary recommendation artifact

REFINEMENT_ARBITRATOR is not responsible for final PM routing arbitration between multiple executable targets. It is responsible for fit signaling.

## Required Explanation Rule

Every decision must include a short justification summary.

The summary must explain:

- why the packet received the recommended action
- what major score pattern drove the decision
- whether engine invocation was needed or skipped
- whether a child-core fit dominated the decision

## Illegal Decision Behavior

REFINEMENT_ARBITRATOR must never:

- use undefined recommendation labels
- emit a decision with no visible score basis
- pass packets solely because they seem interesting
- use Rosetta polish as a substitute for weak reasoning value
- use Curved Mirror weight as a substitute for child-core fit
- act as PM routing authority
- directly trigger child-core execution

## Summary

The decision policy ensures that REFINEMENT_ARBITRATOR remains a bounded gate that decides refinement worth and downstream readiness without blurring into memory, routing, or execution authority.