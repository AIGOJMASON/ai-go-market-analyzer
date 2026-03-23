# CASE CLOSEOUT LAYER

## Purpose

The case closeout layer is the governed final archive surface for one
runtime case.

It exists to consume one approved `case_resolution`, one approved
`child_core_dispatch_packet`, and one approved `child_core_intake_receipt`,
then emit one `case_closeout_record` that seals the runtime-to-child-core
handoff lifecycle.

This layer does not resolve truth.
This layer does not re-route dispatch.
This layer does not execute child-core domain logic.

It archives final lifecycle state only.

---

## Runtime Role

The case closeout layer sits downstream of:

- case resolution
- child-core dispatch packet
- child-core intake receipt

It sits upstream of:

- operator review
- archive surfaces
- later reporting or analytics layers

Its role is to answer:

- is this case lifecycle complete enough to close
- what is the final closeout state
- what evidence seals the runtime-to-child-core handoff path

---

## Structural Rule

Case closeout may:

- validate one approved case resolution
- validate one approved dispatch packet
- validate one approved intake receipt
- verify continuity across those artifacts
- emit one governed closeout record

Case closeout may not:

- re-resolve case truth
- alter dispatch routing
- alter intake outcome
- invent execution results
- perform child-core domain work

---

## Inputs

Approved inputs:

- `case_resolution`
- `child_core_dispatch_packet`
- `child_core_intake_receipt`

Rules:

- all three artifacts are required
- all three artifacts must be sealed
- all three artifacts must share one case id
- dispatch packet must reference the same case_resolution
- intake receipt must reference the same dispatch packet and case_resolution
- closeout state must be derived only from governed upstream artifacts

---

## Output

Approved output:

- `case_closeout_record`

This artifact provides:

- one closeout record id
- one source case id
- one source case resolution id
- one dispatch packet reference
- one intake receipt reference
- one final closeout state
- continuity and evidentiary fields carried forward when lawful
- sealing metadata

This output is archival closeout only.

---

## Closeout States

Approved closeout states:

- `closed_accepted`
- `closed_rejected`

Rules:

- accepted intake produces `closed_accepted`
- rejected intake produces `closed_rejected`

This layer does not infer anything beyond governed intake evidence.

---

## Why This Layer Exists

Without this layer, the system would end with separate artifacts for:

- final truth
- downstream dispatch
- child-core intake acknowledgement

That would leave the final lifecycle state fragmented across multiple
objects and force later consumers to reconstruct closure themselves.

The case closeout layer prevents that by creating one final archive
artifact for the full runtime-to-child-core handoff path.

---

## Enforcement Rules

This layer enforces:

- strict artifact-type validation
- required payload presence
- sealed artifact requirements
- cross-artifact continuity
- internal field leakage blocking
- one final closeout state
- no mutation of source artifacts

---

## Final Constraint

This layer answers:

- what is the final archived closeout state of this case
- which dispatch and intake artifacts sealed the handoff path
- what final truth was in effect at closeout time

This layer does not answer:

- whether child-core execution later succeeded
- whether the case should be reopened
- whether dispatch should be re-routed