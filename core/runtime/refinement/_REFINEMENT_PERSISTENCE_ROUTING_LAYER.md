# REFINEMENT PERSISTENCE ROUTING LAYER

## What it is

The Refinement Persistence Routing layer is the governed storage and consumer-routing boundary for promoted refinement artifacts.

It determines:
- where promoted refinement outputs are allowed to persist
- which downstream consumer classes are allowed to receive them
- what must remain visible but not distributed

This layer does NOT learn.

This layer does NOT alter policy.

This layer does NOT mutate promoted refinement content.

It only validates, classifies, and routes durable refinement outputs into bounded persistence form.

---

## Core function

Consumes:
- `refinement_promotion_record`

Produces:
- `refinement_persistence_route_record`

---

## Why it exists

Upstream stages can now:
- select candidates
- score candidates
- arbitrate candidate outcomes
- promote approved items for controlled persistence

But promotion alone does not answer:

- where durable refinement truth belongs
- which consumer surfaces may lawfully receive it
- how persistence scope is declared
- how non-promoted items remain visible without distribution

This layer answers those questions.

---

## Authority boundary

This layer:
- does NOT learn
- does NOT reweight
- does NOT infer causality
- does NOT change policy
- does NOT mutate promoted items

This layer ONLY:
- validates promotion outputs
- classifies promoted items for persistence
- declares allowed route targets
- emits a sealed routing artifact

---

## Routing model

Only promoted items may be routed for persistence distribution.

Overflow-not-promoted, deferred-visible, and rejected-visible items remain visible in lineage but are not routed as durable consumer inputs.

Routing is deterministic and bounded.

---

## Routing rules

Persistence eligibility:
- item must have `promotion_status == "promoted"`

Allowed route classes:
- `refinement_archive`
- `refinement_review_surface`
- `refinement_governance_memory`

Route cap:
- max 3 routed promoted items per batch

Routing order:
1. higher total score
2. candidate type priority
3. lexical candidate-value fallback

Default route assignment:
- every routed item goes to `refinement_archive`
- every routed item goes to `refinement_review_surface`
- items with total_score >= 5 also go to `refinement_governance_memory`

---

## Candidate priority

1. `pattern_note`
2. `target_child_core_count`
3. `closeout_count`
4. `intake_count`

---

## Output contract

`refinement_persistence_route_record` must:
- be sealed
- include only routed promoted items
- expose route targets per item
- expose counts
- expose unrouted visible sections
- preserve lineage to promotion stage

---

## Failure protection

Reject:
- unsealed inputs
- invalid artifact types
- missing required fields
- internal field leakage
- malformed promoted items
- invalid promotion status
- invalid decision values

---

## System role

This is the first durable routing declaration layer in refinement.

Promotion says:
- this approved item may persist forward

Persistence routing says:
- this promoted item may persist here, and only these consumers may see it