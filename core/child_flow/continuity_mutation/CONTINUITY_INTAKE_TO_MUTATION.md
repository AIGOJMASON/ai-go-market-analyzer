# Stage 26 → Stage 27 Contract

## Input Artifact

`continuity_intake_receipt`

This is the only lawful Stage 27 input.

---

## Required Fields

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

---

## Contract Law

- only accepted continuity intake may pass
- no reinterpretation is allowed
- lineage must be preserved
- no additional narrative payload is required
- the incoming `policy_version` identifies the Stage 26 intake policy version
- Stage 27 validates that upstream policy version for compatibility
- Stage 27 records its own mutation policy version separately in its output receipt

---

## Output

Stage 27 emits one of:
- `continuity_mutation_receipt`
- `continuity_mutation_failure_receipt`