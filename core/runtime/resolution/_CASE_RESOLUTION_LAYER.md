# CASE RESOLUTION LAYER

## Purpose

The case resolution layer is the governed final-state surface for one
runtime case.

It exists to consume one approved `audit_replay_index` and collapse its
branch history into one exclusive, authoritative `case_resolution`
artifact.

This layer does not execute.
This layer does not retry.
This layer does not escalate.
This layer does not dispatch to child cores.

It decides final runtime truth only.

---

## Runtime Role

The case resolution layer sits downstream of:

- audit / replay index

It sits upstream of:

- closeout
- operator review
- child-core dispatch preparation

Its role is to answer:

- what is the final state of this case
- which branch is authoritative
- is the case actionable downstream

---

## Structural Rule

Case resolution may:

- validate one approved audit replay index
- verify replay continuity and branch legality
- select one authoritative source path
- collapse replay history into one exclusive final state
- expose bounded actionability
- emit one governed case-resolution artifact

Case resolution may not:

- execute
- retry
- escalate
- mutate replay history
- reopen earlier branches
- dispatch to child cores
- invent instructions beyond bounded final-state declaration

---

## Input

Approved input:

- `audit_replay_index`

Rules:

- one audit replay index is required
- replay chain must not be empty
- replay chain must begin with the primary branch
- replay chain may contain at most one primary, one retry, and one escalation branch
- the index must be sealed
- the replay chain must belong to one case

---

## Output

Approved output:

- `case_resolution`

This artifact provides:

- one case resolution id
- one source case id
- one exclusive final state
- one authoritative source path
- one authoritative receipt reference
- bounded actionability
- continuity fields carried forward when lawful
- closure metadata

---

## Final States

Approved final states:

- `success`
- `retry_resolved`
- `escalated`
- `terminal_failure`

Only one final state may be emitted.

---

## Resolution Logic

The layer determines final truth from the replay chain.

Typical paths:

1. primary branch succeeded
   - final state: `success`

2. primary branch failed, retry branch succeeded
   - final state: `retry_resolved`

3. primary branch failed, retry branch failed, escalation branch completed
   - final state: `escalated`

4. final observed branch failed without later successful branch
   - final state: `terminal_failure`

This layer selects truth from governed history.
It does not speculate beyond that history.

---

## Why This Layer Exists

Without this layer, downstream systems would need to inspect:

- delivery outcome receipt
- retry outcome receipt
- escalation outcome receipt
- audit replay index

and then infer final truth themselves.

That would leak resolution authority downstream.

The case resolution layer prevents that by creating one authoritative
final-state object for later use.

---

## Enforcement Rules

This layer enforces:

- strict artifact-type validation
- required payload presence
- replay-chain continuity
- branch uniqueness
- internal field leakage blocking
- one exclusive final state
- no dispatch authority
- no mutation of replay input

---

## Final Constraint

This layer answers:

- what is the final truth of this case
- which path became authoritative
- whether the outcome is actionable downstream

This layer does not answer:

- which child core should receive the case
- what domain-specific action should be taken
- how dispatch should occur