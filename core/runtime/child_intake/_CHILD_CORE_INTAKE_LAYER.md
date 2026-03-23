# CHILD-CORE INTAKE LAYER

## Purpose

The child-core intake layer is the governed acknowledgement surface at
the child-core boundary.

It exists to consume one approved `child_core_dispatch_packet` and one
bounded intake decision, then emit one `child_core_intake_receipt`
confirming lawful downstream acceptance or rejection.

This layer does not resolve truth.
This layer does not re-route dispatch.
This layer does not execute child-core domain logic.

It records intake only.

---

## Runtime Role

The child-core intake layer sits downstream of:

- child-core dispatch packet

It sits upstream of:

- child-core execution
- child-core intake tracking
- later closeout and operator review surfaces

Its role is to answer:

- was dispatch lawfully received
- did the target child core accept intake
- what intake status now governs the child-core boundary

---

## Structural Rule

Child-core intake may:

- validate one approved child-core dispatch packet
- validate one bounded intake decision
- emit one governed intake receipt

Child-core intake may not:

- re-resolve case truth
- alter dispatch packet contents
- change the target child core
- invent execution results
- perform child-core domain work

---

## Inputs

Approved inputs:

- `child_core_dispatch_packet`
- `intake_decision`
- optional `intake_reason`
- optional `accepted_by`

Approved intake decisions:

- `accepted`
- `rejected`

Rules:

- child_core_dispatch_packet is required
- the dispatch packet must be sealed
- the dispatch packet must be dispatch_ready
- the target child core must be approved
- the intake decision must be bounded and explicit
- if rejected, an intake_reason is required

---

## Output

Approved output:

- `child_core_intake_receipt`

This artifact provides:

- one intake receipt id
- one source case id
- one source dispatch packet id
- one target child core
- one intake status
- one downstream intake authority marker
- lawful continuity fields carried forward when present
- sealing metadata

This output is acknowledgement only.

---

## Why This Layer Exists

Without this layer, dispatch would imply intake silently.

That would create hidden state at the child-core boundary and break the
system rule that every meaningful transition must be receipted.

The child-core intake layer prevents that by creating one explicit,
governed receipt confirming whether the child-core boundary accepted or
rejected the dispatch packet.

---

## Enforcement Rules

This layer enforces:

- strict artifact-type validation
- required payload presence
- sealed dispatch requirement
- dispatch_ready requirement
- approved target requirement
- explicit intake decision requirement
- rejection reason requirement when rejected
- internal field leakage blocking
- no mutation of source dispatch packet

---

## Final Constraint

This layer answers:

- was the dispatch packet received lawfully
- did the target child core accept intake
- what is the intake status at the child-core boundary

This layer does not answer:

- whether child-core execution succeeded
- what the child core produced
- whether downstream work should be re-routed