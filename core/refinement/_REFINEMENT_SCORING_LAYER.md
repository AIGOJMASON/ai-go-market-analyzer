# REFINEMENT SCORING LAYER

## What it is

The Refinement Scoring layer is the second governed boundary in the refinement path.

It sits after:
- `analytics_summary`
- `refinement_candidate_set`

It sits before:
- refinement arbitration
- any future weighting approval
- any future governed learning surface

This layer does NOT learn.

This layer does NOT mutate upstream truth.

This layer assigns bounded, deterministic scores to already selected refinement candidates.

---

## Core function

Consumes:
- `refinement_candidate_set`

Produces:
- `refinement_scoring_record`

---

## Why it exists

Selection alone is not enough.

Once candidates are admitted, the system still needs a lawful method to say:

- which candidates are stronger
- which candidates are broader
- which candidates are weaker
- which candidates should remain visible but lower-priority

Without this layer:
- all selected candidates remain flat
- downstream arbitration must improvise its own weighting logic
- scoring drift begins too early

This layer prevents that.

---

## Authority boundary

This layer:
- does NOT learn
- does NOT infer causality
- does NOT alter routing
- does NOT update policy
- does NOT reweight the system

This layer ONLY:
- validates candidate-set structure
- scores candidates using explicit deterministic rules
- returns a sealed scoring artifact

---

## Scoring philosophy

Scores are assigned from observable structural properties only.

Allowed signals:
- candidate type
- source field
- candidate value shape
- count magnitude
- pattern-note presence
- retrieval-context presence

Disallowed signals:
- intuition
- semantic interpretation
- speculative forecasting
- hidden inference
- narrative judgment

---

## Deterministic scoring model

The scoring model is bounded and additive.

Base score depends on candidate type.

Additional score may be granted for:
- positive count magnitude
- retrieval context availability
- recognized pattern-note structure

No score may be granted from hidden fields or interpretation.

---

## Output contract

`refinement_scoring_record` must:
- contain only validated scored candidates
- preserve input candidate identity and type
- expose score components
- expose total score
- remain sealed
- remain read-only

---

## Failure protection

Reject:
- unsealed candidate sets
- invalid artifact types
- missing payload fields
- internal field leakage
- malformed selected candidates
- invalid candidate types
- invalid scoreable values

---

## System role

This is the final bounded preparation layer before refinement arbitration.

Selection says:
- this may matter

Scoring says:
- this matters more or less, and here is why

That distinction must remain explicit.