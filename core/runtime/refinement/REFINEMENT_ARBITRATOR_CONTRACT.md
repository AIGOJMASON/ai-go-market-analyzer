# REFINEMENT ARBITRATOR CONTRACT

## Purpose

Define the governed Stage 16 refinement arbitrator layer for AI_GO runtime.

This layer consumes already-bounded runtime facts and historical refinement signals,
then emits one bounded refinement packet for operator or PM-facing interpretation.

It does not mutate execution, routing, candidate selection, or recommendation generation.

---

## Inputs

The arbitrator may consume only bounded artifacts or normalized runtime facts, including:

- accepted closeout records
- quarantined closeout records
- historical analog panel
- market panel
- governance panel
- recommendation panel
- refinement intake index
- learning promotion index

It may not inspect raw ingress directly unless that ingress has already been normalized into a governed packet.

---

## Output

The arbitrator emits one sealed artifact:

- `refinement_arbitrator_packet`

---

## Non-authority rule

This layer may:

- annotate
- compress
- weight
- summarize
- flag risk
- adjust interpretation confidence

This layer may not:

- create or remove candidates
- alter execution permissions
- override watcher
- modify recommendation entries
- write to persistence as a side effect of evaluation
- bypass PM governance

---

## Required output fields

A valid `refinement_arbitrator_packet` contains:

- `artifact_type`
- `artifact_version`
- `sealed`
- `core_id`
- `refinement_mode`
- `confidence_adjustment`
- `risk_flags`
- `reasoning_summary`
- `narrative_summary`
- `source_lineage`

Optional bounded support fields:

- `analog_signal`
- `historical_failure_bias`
- `historical_success_bias`
- `notes`

---

## Decision philosophy

The arbitrator is not a predictor.

It is a bounded interpretation layer that answers:

- what prior governed outcomes say about this shape
- whether historical analog evidence increases or decreases confidence
- whether failure memory should surface a caution flag
- how to present that to an operator without mutating the decision pipeline

---

## Allowed confidence adjustments

- `up`
- `down`
- `none`

---

## Allowed refinement modes

- `annotation_only`
- `confidence_conditioning`

---

## Risk flag examples

- `early_reversal_likelihood`
- `weak_confirmation_history`
- `failure_cluster_detected`
- `no_material_refinement_signal`

---

## Integration position

The intended flow is:

live ingress
→ classifier
→ signal stack
→ historical analog
→ watcher / closeout memory
→ refinement arbitrator
→ refinement packet
→ dashboard / PM interpretation

---

## Constraint law

All arbitrator behavior must follow:

input → bounded interpretation → sealed output → no side effects