# Stage 27 → Stage 28 Contract

## Input Artifact

`continuity_read_request`

This is the only lawful Stage 28 input.

Stage 28 reads continuity state written by Stage 27 but does not accept raw mutation receipts as its request surface.

---

## Required Fields

- `request_type`
- `request_id`
- `requesting_surface`
- `consumer_profile`
- `target_core`
- `continuity_scope`
- `read_reason`
- `requested_view`
- `policy_version`
- `timestamp`

---

## Contract Law

- only valid continuity read requests may enter Stage 28
- Stage 28 may read continuity state but may not mutate it
- requester, consumer profile, target, scope, and view must all be policy-valid
- Stage 28 must emit a bounded artifact, hold receipt, or failure receipt
- no raw continuity-store exposure is allowed

---

## Output

Stage 28 emits one of:
- `continuity_distribution_artifact` plus `continuity_distribution_receipt`
- `continuity_distribution_hold_receipt`
- `continuity_distribution_failure_receipt`