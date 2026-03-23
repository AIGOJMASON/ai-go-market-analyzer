# REFINEMENT PROMOTION LAYER

## What it is

The Refinement Promotion layer is the controlled promotion boundary of the refinement pipeline.

It converts approved refinement decisions into a governed promotion artifact that can be consumed by later system surfaces.

This layer does NOT perform free learning.

This layer does NOT mutate model weights.

This layer does NOT alter routing logic.

It only promotes already-approved refinement outcomes into a bounded, durable, downstream-safe form.

---

## Core function

Consumes:
- `refinement_decision_record`

Produces:
- `refinement_promotion_record`

---

## Why it exists

Upstream stages can now:
- detect patterns
- select candidates
- score candidates
- arbitrate candidate outcomes

But that still does not answer:

- what is allowed to persist
- what is allowed to become downstream input
- what must remain non-durable
- what must stop at arbitration

This layer answers those questions.

---

## Authority boundary

This layer:
- does NOT learn
- does NOT reweight
- does NOT infer causality
- does NOT change policy
- does NOT mutate upstream truth

This layer ONLY:
- validates decision outputs
- promotes approved items
- rejects non-approved items from durable promotion
- emits a sealed promotion record

---

## Promotion model

Only candidates already marked `approved` may be promoted.

Deferred and rejected items remain visible in lineage, but they are not promoted.

Promotion is deterministic and bounded.

---

## Promotion rules

Promotion eligibility:
- candidate decision must be `approved`

Promotion cap:
- max 3 promoted items per batch

Promotion order:
1. higher total score
2. candidate type priority
3. lexical candidate-value fallback

Promotion output must include:
- original candidate fields
- score
- decision
- promotion status
- promotion reason
- lineage source

---

## Candidate priority

1. `pattern_note`
2. `target_child_core_count`
3. `closeout_count`
4. `intake_count`

---

## Output contract

`refinement_promotion_record` must:
- be sealed
- include only promoted approved items
- expose counts
- expose non-promoted approved overflow items
- expose promotion notes
- preserve lineage to refinement decision stage

---

## Failure protection

Reject:
- unsealed inputs
- invalid artifact types
- missing required fields
- internal field leakage
- malformed decision items
- invalid decision values

---

## System role

This is the first controlled durability surface in refinement.

Selection says:
- this may matter

Scoring says:
- this matters more or less

Arbitration says:
- this is approved, deferred, or rejected

Promotion says:
- this approved item is allowed to persist forward in governed form