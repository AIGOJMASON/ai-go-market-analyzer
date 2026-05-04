
---

# `AI_GO/engines/refinement_arbitrator/WEIGHTING_MODEL.md`

```md
# REFINEMENT_ARBITRATOR Weighting Model

## Purpose

This document defines how REFINEMENT_ARBITRATOR computes downstream propagation value.

The model exists so arbitration is not subjective, hidden, or prose-only. It must remain inspectable and stable.

## Scoring Principle

A research packet does not move downstream because it merely exists.

It moves downstream because it earns sufficient composite weight under bounded scoring.

Composite weight is formed from three scored components:

1. reasoning weight
2. human tempering weight
3. child-core fit score

## Score Range

All scores use a normalized range from 0.00 to 1.00.

Interpretation:

- 0.00 to 0.24 = negligible
- 0.25 to 0.49 = weak
- 0.50 to 0.69 = moderate
- 0.70 to 0.84 = strong
- 0.85 to 1.00 = high

## Component Definitions

### Reasoning Weight

Reasoning weight estimates structural worth.

Primary source: Curved Mirror

Factors may include:

- domain specificity
- structural coherence
- repeatability
- downstream utility
- reasoning stability
- evidence alignment

### Human Tempering Weight

Human tempering weight estimates presentation and interpretive usefulness.

Primary source: Rosetta

Factors may include:

- clarity
- human-facing interpretability
- communicative value
- presentation usefulness
- narrative usability for downstream human-facing cores

### Child-Core Fit Score

Child-core fit score estimates how well the packet aligns with a specific child core’s operating needs.

Factors may include:

- domain match
- task suitability
- profile-weight compatibility
- contamination risk
- expected downstream usefulness
- historical fit policy if later enabled by governed continuity

## Composite Formula

For a given child core, composite weight is:

CompositeWeight(core) =
  (ReasoningWeight × R)
+ (HumanTemperingWeight × H)
+ (ChildCoreFitScore(core) × C)

Where:

- R = reasoning coefficient
- H = human tempering coefficient
- C = child-core fit coefficient

Constraint:

R + H + C = 1.00

## Default Coefficients

System default when no child-core profile overrides exist:

- R = 0.40
- H = 0.20
- C = 0.40

This keeps the system balanced between structural value and core-specific utility, while preventing purely polished but irrelevant signal from propagating.

## Profile Override Rule

A child core may override the default coefficients through its governed profile.

Examples:

### Reasoning-heavy core example

contractor_proposals_core:

- R = 0.50
- H = 0.15
- C = 0.35

### GIS-heavy core example

louisville_gis_core:

- R = 0.55
- H = 0.10
- C = 0.35

### Narrative-heavy future core example

writing_core:

- R = 0.25
- H = 0.35
- C = 0.40

These are examples only unless locked elsewhere by profile files.

## Threshold Bands

Composite weight should map to decision bands.

Default decision bands:

- 0.00 to 0.29 = discard
- 0.30 to 0.49 = hold
- 0.50 to 0.64 = condition_for_child_core
- 0.65 to 0.79 = send_to_engine_or_pass_to_pm_based_on_gap
- 0.80 to 1.00 = pass_to_pm

These bands may be tightened by policy when entropy is high.

## Gap Logic

High composite score does not always mean immediate pass_to_pm.

The arbitrator must also evaluate whether the packet is missing one required refinement dimension.

Example:

- reasoning strong
- core fit strong
- human tempering weak

In that case recommended_action may be:

- send_to_rosetta

Likewise:

- human tempering moderate
- core fit moderate
- reasoning weak

Recommended action may be:

- send_to_curved_mirror

## Entropy Adjustment Rule

When entropy is high, the system must become more conservative.

Suggested enforcement:

- raise discard threshold
- narrow pass_to_pm threshold
- prefer hold over speculative conditioning
- do not allow weak packets to propagate merely because they are adjacent to useful topics

## Contamination Penalty

If a packet appears structurally useful but cross-domain contamination risk is high, apply a fit penalty.

Example penalty model:

AdjustedFitScore = RawFitScore - ContaminationPenalty

Where contamination penalty may range from 0.05 to 0.30 depending on severity.

This prevents bleed between child cores with different operating truths.

## Missing Score Rule

If a required component is unavailable:

- do not invent it
- mark it missing
- either hold or invoke the missing engine if policy allows

No component may be fabricated for score completion.

## Output Requirement

Every decision must surface:

- reasoning weight
- human tempering weight
- child-core fit score used
- coefficients used
- resulting composite weight
- resulting decision band

## Summary

The weighting model exists to convert research propagation from a vague qualitative act into a bounded, profile-aware, scored governance step.