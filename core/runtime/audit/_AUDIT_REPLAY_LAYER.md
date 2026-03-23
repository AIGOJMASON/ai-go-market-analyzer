# AUDIT / REPLAY LAYER

## Purpose

The audit / replay layer is the governed consolidation surface for
runtime outcome history.

It exists to unify already-issued runtime outcome receipts into a
single replayable chain for one case without introducing resolution,
dispatch, or downstream interpretation authority.

This layer does not decide final truth.
This layer does not invent state.
This layer does not mutate upstream receipts.

---

## Runtime Role

The audit / replay layer sits downstream of:

- delivery outcome receipt
- retry outcome receipt
- escalation outcome receipt

It sits upstream of:

- case resolution
- closeout
- operator review
- child-core dispatch preparation

Its role is to expose one governed, replayable chain for the full
runtime path of a case.

---

## Structural Rule

Audit / replay may:

- validate approved receipt types
- verify case continuity
- normalize branch history
- order branch entries into one replay chain
- emit one governed audit replay index

Audit / replay may not:

- execute
- retry
- escalate
- resolve final truth
- choose child-core action
- reinterpret source outcomes beyond structural consolidation

---

## Inputs

Approved inputs:

- `delivery_outcome_receipt`
- `retry_outcome_receipt`
- `escalation_outcome_receipt`

Rules:

- delivery outcome receipt is required
- retry outcome receipt is optional
- escalation outcome receipt is optional
- all provided receipts must share one case id
- only one receipt per branch class may be provided

---

## Output

Approved output:

- `audit_replay_index`

This artifact provides:

- one audit replay index id
- one source case id
- one ordered replay chain
- receipt references for each observed branch
- continuity fields when shared across receipts
- sealing metadata

This output is structural history only.

---

## Replay Scope

The replay chain may include:

1. primary delivery outcome
2. retry outcome
3. escalation outcome

The layer records what happened and in what order.

It does not determine which branch is authoritative final truth.

---

## Why This Layer Exists

Without this layer, later stages would need to reconstruct case history
from separate receipts.

That would force downstream logic to:

- gather multiple artifacts
- rebuild chronology
- infer branch structure

That would leak authority into later layers.

The audit / replay layer prevents that by creating one governed replay
surface while preserving strict non-resolution boundaries.

---

## Enforcement Rules

This layer enforces:

- strict artifact-type validation
- required payload presence
- case-id continuity
- branch uniqueness
- internal field leakage blocking
- no hidden branch synthesis
- no receipt mutation

---

## Final Constraint

This layer answers:

- what receipts exist for this case
- what order they occurred in
- what governed branches were observed

This layer does not answer:

- what is the final truth of the case
- what should a child core do next