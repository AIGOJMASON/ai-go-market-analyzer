# REFINEMENT PERSISTENCE COMMIT LAYER

## What it is

The Refinement Persistence Commit layer is the governed durable-write boundary for routed refinement outputs.

It converts routing declarations into explicit persistence commit receipts.

This layer does NOT learn.

This layer does NOT alter refinement content.

This layer does NOT reinterpret routing policy.

It only validates routing declarations, records durable commit intent/outcome in bounded form, and emits a sealed commit artifact.

---

## Core function

Consumes:
- `refinement_persistence_route_record`

Produces:
- `refinement_persistence_commit_record`

---

## Why it exists

Upstream stages can now:
- select candidates
- score candidates
- arbitrate outcomes
- promote approved items
- declare allowed persistence routes

But routing declaration is not the same as actual durable commit.

This layer answers:

- what was actually committed
- which route targets were actually written
- which routed items remain visible but uncommitted
- what receipt proves the commit event occurred

---

## Authority boundary

This layer:
- does NOT learn
- does NOT reweight
- does NOT infer causality
- does NOT change policy
- does NOT mutate routed items

This layer ONLY:
- validates route records
- converts routed items into commit receipts
- preserves visible non-routed lineage
- emits a sealed persistence commit artifact

---

## Commit model

Only routed items may be committed.

Non-routed visible sections remain visible in lineage but are not committed.

Commit is deterministic and bounded.

---

## Commit rules

Commit eligibility:
- item must have `route_status == "routed"`

Commit result:
- eligible routed items receive `commit_status == "committed"`

Commit targets:
- copied directly from lawful `route_targets`

Commit receipt must include:
- original routed item fields
- route status
- route targets
- commit status
- commit reason
- lineage source

---

## Output contract

`refinement_persistence_commit_record` must:
- be sealed
- include only committed routed items
- expose committed counts
- expose visible non-committed sections
- expose commit notes
- preserve lineage to persistence routing stage

---

## Failure protection

Reject:
- unsealed inputs
- invalid artifact types
- missing required fields
- internal field leakage
- malformed routed items
- invalid route status
- invalid route targets
- invalid decision values
- invalid promotion status

---

## System role

This is the durable proof layer in refinement.

Routing says:
- this promoted item may persist here

Commit says:
- this routed item did persist here, and this receipt proves it