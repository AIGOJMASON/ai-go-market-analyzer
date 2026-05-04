# Stage 28 Closeout Probe

## Purpose

This probe validates Stage 28 as the lawful continuity read and distribution boundary with named consumer profiles.

It confirms that Stage 28:
- accepts only `continuity_read_request`
- validates request structure
- validates consumer-profile legality
- validates requester legality through the consumer profile
- validates target legality
- validates continuity-scope legality
- validates requested-view legality
- validates policy-version compatibility
- reads continuity state without mutating it
- emits bounded distribution artifacts and receipts
- applies profile-based shaping and record limits
- updates only minimal distribution state

---

## Test Cases

### Case 1 — valid pm_core_reader latest_n_records request → fulfilled
Expected:
- `continuity_distribution_artifact`
- `continuity_distribution_receipt`
- consumer profile recorded
- record_count <= profile maximum

### Case 2 — valid child_core_reader latest_record request → fulfilled
Expected:
- `continuity_distribution_artifact`
- `continuity_distribution_receipt`
- refs-only shaping enforced by profile
- record_count <= 1

### Case 3 — invalid request type → failure
Expected:
- `continuity_distribution_failure_receipt`
- `rejection_code = invalid_input`

### Case 4 — invalid consumer profile → failure
Expected:
- `continuity_distribution_failure_receipt`
- `rejection_code = consumer_profile_unlawful`

### Case 5 — invalid requester for profile → failure
Expected:
- `continuity_distribution_failure_receipt`
- `rejection_code = requester_unlawful`

### Case 6 — invalid target for profile → failure
Expected:
- `continuity_distribution_failure_receipt`
- target-related rejection

### Case 7 — invalid scope → failure
Expected:
- `continuity_distribution_failure_receipt`
- `rejection_code = scope_unlawful`

### Case 8 — invalid view for profile → failure
Expected:
- `continuity_distribution_failure_receipt`
- `rejection_code = view_unlawful`

### Case 9 — invalid policy version → failure
Expected:
- `continuity_distribution_failure_receipt`
- `rejection_code = policy_version_invalid`

---

## Closeout Standard

Stage 28 passes only when all cases return the expected bounded result and continuity state remains read-only during distribution.