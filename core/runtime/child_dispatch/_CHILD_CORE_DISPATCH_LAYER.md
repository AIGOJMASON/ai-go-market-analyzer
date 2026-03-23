# CHILD-CORE DISPATCH LAYER

## Purpose

The child-core dispatch layer is the governed handoff surface between
resolved runtime truth and downstream child-core consumption.

It exists to consume one approved `case_resolution`, apply bounded
dispatch policy, and emit one `child_core_dispatch_packet` for one
approved child core.

This layer does not resolve truth.
This layer does not inspect branch receipts.
This layer does not execute child-core domain logic.

It prepares lawful downstream handoff only.

---

## Runtime Role

The child-core dispatch layer sits downstream of:

- case resolution

It sits upstream of:

- child-core intake
- child-core execution
- later operator review or closeout surfaces

Its role is to answer:

- may this resolved case be dispatched
- which approved child core may receive it
- what bounded instruction class should accompany the handoff

---

## Structural Rule

Child-core dispatch may:

- validate one approved case resolution
- validate one approved child-core target
- enforce dispatch policy
- emit one bounded child-core dispatch packet

Child-core dispatch may not:

- re-resolve case truth
- inspect raw replay history
- inspect raw branch receipts
- alter final state
- execute child-core logic
- invent broad domain instructions outside policy

---

## Input

Approved inputs:

- `case_resolution`
- one approved child-core target
- optional dispatch note

Rules:

- case resolution is required
- case resolution must be sealed
- case resolution must be actionable
- target child core must be approved by dispatch policy
- payload class and route class must be allowed for that target
- only one child-core target may be selected per dispatch packet

---

## Output

Approved output:

- `child_core_dispatch_packet`

This artifact provides:

- one dispatch packet id
- one source case id
- one source case resolution id
- one approved child-core target
- one bounded instruction
- carried continuity fields when lawful
- dispatch readiness metadata

This output is downstream handoff only.

---

## Why This Layer Exists

Without this layer, child cores would need to:

- inspect case resolution directly
- infer whether dispatch is permitted
- infer whether their core is an approved recipient
- decide their own instruction class

That would leak routing and dispatch authority downstream.

The child-core dispatch layer prevents that by creating one governed,
bounded handoff packet for one approved child core.

---

## Enforcement Rules

This layer enforces:

- strict artifact-type validation
- required payload presence
- sealed case-resolution requirement
- actionable requirement
- target approval by policy
- payload-class and route-class compatibility
- internal field leakage blocking
- one target per packet
- no mutation of source resolution

---

## Final Constraint

This layer answers:

- may this resolved case be dispatched
- which approved child core receives it
- what bounded instruction accompanies the handoff

This layer does not answer:

- whether the case truth is correct
- how the child core should internally solve the task
- whether the child core should further delegate