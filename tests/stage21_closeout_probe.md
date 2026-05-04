# Stage 21 Closeout Probe

## Purpose
Verify that child-core ingress handoff behaves lawfully under bounded Stage 21 rules.

## Scope
This probe validates:

- binary ingress readiness enforcement
- correct ingress receipt emission
- rejection of unknown target cores
- rejection of destination-surface mismatch
- rejection of missing ingress handlers
- absence of domain execution leakage
- exact minimal state compliance

## Test Coverage

### 1. Valid ingress handoff
- input: valid `dispatch_packet`
- expected:
  - emits `ingress_receipt`
  - preserves target core
  - preserves destination surface
  - invokes declared ingress handler exactly once

### 2. Unknown target core fails
- input: dispatch packet targeting an undeclared child core
- expected:
  - emits `ingress_failure_receipt`
  - reason = `unknown_target_core`

### 3. Destination-surface mismatch fails
- input: dispatch packet whose destination surface does not match the declared surface for the target core
- expected:
  - emits `ingress_failure_receipt`
  - reason = `destination_surface_target_mismatch`

### 4. Missing ingress handler fails
- input: dispatch packet with valid target and surface but no declared ingress handler
- expected:
  - emits `ingress_failure_receipt`
  - reason = `missing_ingress_handler`

### 5. No domain execution leakage
- ingress receipt must contain:
  - no execution result
  - no runtime result
  - no child-core output
  - no final output artifact

### 6. Exact minimal state shape
- ingress state must contain only:
  - `last_ingress_id`
  - `last_target_core`
  - `last_timestamp`

## Pass Condition
All tests must return:

`"passed": true`

## Failure Condition
Any of the following:
- ingress receipt emitted for invalid target or invalid surface
- missing handler allowed through
- domain execution fields present
- state expands beyond allowed surface

## Output
The probe returns a structured JSON result:

```json
{
  "stage": "STAGE_21_CLOSEOUT",
  "status": "complete",
  "results": { ... }
}