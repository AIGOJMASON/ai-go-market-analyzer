# Stage 27 Closeout Probe

## Purpose

This probe validates Stage 27 as the first lawful continuity write boundary.

It confirms that Stage 27:
- accepts only `continuity_intake_receipt`
- validates receipt structure
- validates lineage integrity
- validates target legality
- validates continuity scope legality
- validates upstream intake policy compatibility
- writes only bounded continuity state
- emits only mutation or mutation-failure receipts
- behaves idempotently for duplicate intake
- does not access watcher execution paths
- does not publish child-core outputs

---

## Test Cases

### Case 1 — valid intake → created
Expected:
- `continuity_mutation_receipt`
- `mutation_type = created`

### Case 2 — duplicate intake → no_op
Expected:
- `continuity_mutation_receipt`
- `mutation_type = no_op`

### Case 3 — invalid receipt type → failure
Expected:
- `continuity_mutation_failure_receipt`
- `rejection_code = invalid_input`

### Case 4 — invalid target → failure
Expected:
- `continuity_mutation_failure_receipt`
- `rejection_code = scope_unlawful`

### Case 5 — invalid scope → failure
Expected:
- `continuity_mutation_failure_receipt`
- `rejection_code = scope_unlawful`

### Case 6 — upstream policy mismatch → failure
Expected:
- `continuity_mutation_failure_receipt`
- `rejection_code = policy_version_invalid`

### Case 7 — broken lineage → failure
Expected:
- `continuity_mutation_failure_receipt`
- `rejection_code = lineage_broken`

---

## Closeout Standard

Stage 27 passes only when all cases return the expected bounded result and no mutation occurs outside the continuity store.