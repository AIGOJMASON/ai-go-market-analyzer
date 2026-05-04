# Stage 27 — Continuity Mutation Policy

## Allowed Input

Only:
- `continuity_intake_receipt`

All other input artifacts are rejected.

---

## Required Input Fields

The incoming `continuity_intake_receipt` must contain:
- `receipt_type`
- `intake_id`
- `target_core`
- `continuity_scope`
- `admission_basis`
- `watcher_receipt_ref`
- `output_disposition_ref`
- `runtime_ref`
- `policy_version`
- `timestamp`

The `policy_version` in the incoming receipt is the Stage 26 intake policy version.
It is not the Stage 27 mutation policy version.

---

## Mutation Classes

### 1. created
No existing continuity record is present for the incoming continuity key.

### 2. updated
An existing record is present and is lawfully advanced in place.

### 3. merged
Multiple continuity records are consolidated into a single governed record.

### 4. no_op
Incoming continuity is duplicate, already represented, or superseded without requiring a state change.

### 5. mutation_failed
Structural, registry, lineage, or mutation-policy failure prevented write.

---

## Required Checks

### 1. Receipt Integrity
- `receipt_type` must equal `continuity_intake_receipt`

### 2. Lineage Integrity
The incoming receipt must include non-empty:
- `watcher_receipt_ref`
- `output_disposition_ref`
- `runtime_ref`

### 3. Target Legality
- `target_core` must be registered
- `continuity_scope` must be allowed for the registered target

### 4. Upstream Intake Policy Compatibility
- incoming `policy_version` must be one of the allowed Stage 26 intake policy versions for the target

### 5. Duplicate / Supersession Control
- duplicate continuity writes must not create duplicate records

### 6. Write Boundedness
- no unbounded expansion
- no freeform narrative mutation
- no state written outside the allowed continuity surface

---

## Rejection Conditions

Reject mutation when:
- receipt type is invalid
- required fields are missing or malformed
- lineage is broken
- target is unlawful
- scope is unlawful
- upstream intake policy version is invalid
- mutation policy blocks write

---

## Mutation Rules

- writes must be deterministic
- writes should be idempotent when possible
- no mutation without lineage trace
- duplicate exact intake should resolve to `no_op`
- successful mutation receipts must record Stage 27 mutation policy version