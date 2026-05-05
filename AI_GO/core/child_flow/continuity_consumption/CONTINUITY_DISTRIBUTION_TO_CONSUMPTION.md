# Stage 28 → Stage 29 Contract

## Input Artifacts

Stage 29 consumes:
- `continuity_distribution_artifact`
- `continuity_distribution_receipt`

Both are required for automatic fulfillment.

---

## Required Artifact Fields

- `artifact_type`
- `distribution_id`
- `target_core`
- `continuity_scope`
- `requested_view`
- `consumer_profile`
- `records`
- `record_count`
- `timestamp`

---

## Required Receipt Fields

- `receipt_type`
- `distribution_receipt_id`
- `request_id`
- `target_core`
- `requesting_surface`
- `consumer_profile`
- `requested_view`
- `artifact_id`
- `policy_version`
- `timestamp`

---

## Contract Law

- Stage 29 may consume only lawful Stage 28 outputs
- Stage 29 may not read raw continuity store directly
- Stage 29 must validate artifact / receipt alignment
- Stage 29 must preserve consumer-profile legality
- Stage 29 may emit only a bounded downstream packet or a hold/failure receipt

---

## Output

Stage 29 emits one of:
- `continuity_strategy_packet` plus `continuity_consumption_receipt`
- `continuity_consumption_hold_receipt`
- `continuity_consumption_failure_receipt`