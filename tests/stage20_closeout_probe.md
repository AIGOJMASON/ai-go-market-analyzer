# Stage 20 Closeout Probe

## Purpose
Verify that PM routing-to-dispatch handoff behaves lawfully under bounded Stage 20 rules.

## Scope
This probe validates:

- binary dispatch readiness enforcement
- correct dispatch packet emission
- rejection of candidate-set ambiguity at dispatch
- rejection of unknown targets
- rejection of missing destination surfaces
- absence of child-core internal execution leakage
- exact minimal state compliance

## Test Coverage

### 1. Valid single-target dispatch
- input: valid `pm_routing_packet` with `target_mode = single`
- expected:
  - emits `dispatch_packet`
  - preserves target core
  - preserves destination surface

### 2. Candidate-set routing is not dispatchable
- input: valid `pm_routing_packet` with `target_mode = candidate_set`
- expected:
  - emits `dispatch_failure_receipt`
  - reason = `candidate_set_not_dispatchable`

### 3. Unknown target fails
- input: routing packet targeting an undeclared child core
- expected:
  - emits `dispatch_failure_receipt`
  - reason = `unknown_target`

### 4. Missing destination surface fails
- input: routing packet with valid target but no declared destination surface
- expected:
  - emits `dispatch_failure_receipt`
  - reason = `missing_destination_surface`

### 5. No child-core execution leakage
- dispatch packet must contain:
  - no execution result
  - no activated core marker
  - no runtime output payload
  - no child-core output data

### 6. Exact minimal state shape
- dispatch state must contain only:
  - `last_dispatch_id`
  - `last_target`
  - `last_timestamp`

## Pass Condition
All tests must return:

`"passed": true`

## Failure Condition
Any of the following:
- dispatch packet emitted for candidate-set ambiguity
- unknown target allowed through
- undeclared destination surface allowed through
- child-core execution fields present
- state expands beyond allowed surface

## Output
The probe returns a structured JSON result:

```json
{
  "stage": "STAGE_20_CLOSEOUT",
  "status": "complete",
  "results": { ... }
}