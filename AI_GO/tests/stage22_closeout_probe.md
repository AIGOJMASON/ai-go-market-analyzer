# Stage 22 Closeout Probe

## Purpose
Verify that child-core runtime handoff behaves lawfully under bounded Stage 22 rules.

## Scope
This probe validates:

- binary runtime readiness enforcement
- correct runtime receipt emission
- rejection when ingress was not accepted
- rejection of unknown target cores
- rejection of execution-surface mismatch
- rejection of missing execution handlers
- absence of output, watcher, and continuity leakage
- exact minimal state compliance

## Test Coverage

### 1. Valid runtime start
- input: valid `ingress_receipt` plus bounded `runtime_context`
- expected:
  - emits `runtime_receipt`
  - preserves target core
  - preserves execution surface
  - preserves bounded `result_ref` if returned
  - invokes declared execution handler exactly once

### 2. Ingress not accepted fails
- input: ingress receipt with `handoff_status != accepted`
- expected:
  - emits `runtime_failure_receipt`
  - reason = `ingress_not_accepted`

### 3. Unknown target core fails
- input: ingress receipt for undeclared child core
- expected:
  - emits `runtime_failure_receipt`
  - reason = `unknown_target_core`

### 4. Execution-surface mismatch fails
- input: valid ingress receipt with runtime context whose execution surface does not match target-core declaration
- expected:
  - emits `runtime_failure_receipt`
  - reason = `execution_surface_target_mismatch`

### 5. Missing execution handler fails
- input: valid ingress receipt and valid execution surface with no declared execution handler
- expected:
  - emits `runtime_failure_receipt`
  - reason = `missing_execution_handler`

### 6. No output / watcher / continuity leakage
- runtime receipt must contain:
  - no final output payload
  - no child-core output payload
  - no watcher fields
  - no continuity or SMI fields

### 7. Exact minimal state shape
- runtime state must contain only:
  - `last_runtime_id`
  - `last_target_core`
  - `last_timestamp`

## Pass Condition
All tests must return:

`"passed": true`

## Failure Condition
Any of the following:
- runtime receipt emitted for invalid ingress or invalid execution surface
- missing execution handler allowed through
- output or monitoring fields present
- state expands beyond allowed surface

## Output
The probe returns a structured JSON result:

```json
{
  "stage": "STAGE_22_CLOSEOUT",
  "status": "complete",
  "results": { ... }
}