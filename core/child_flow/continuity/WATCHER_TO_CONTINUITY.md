# WATCHER TO CONTINUITY
## Stage 25 → Stage 26 Handoff Contract

## Purpose
This document defines the lawful handoff from watcher execution to continuity intake.

The handoff is narrow and contract-bound.

Stage 25 produces watcher output.
Stage 26 decides admissibility for continuity intake.

No other authority transfer occurs here.

---

## Handoff Rule
Watcher output does not mutate continuity directly.

Watcher output may only cross into Stage 26 through:
- `watcher_result`
- `continuity_context`

---

## Required Payload

```json
{
  "watcher_result": {
    "findings": {},
    "findings_ref": "optional"
  },
  "continuity_context": {
    "target_core": "string",
    "watcher_id": "string",
    "watcher_receipt_ref": "string",
    "output_disposition_ref": "string",
    "runtime_ref": "string",
    "event_timestamp": "UTC timestamp",
    "continuity_scope": "string",
    "intake_reason": "string",
    "admission_policy_version": "string"
  }
}
watcher_result Rules

findings is mandatory

findings must be a dictionary

findings must not be silently rewritten by Stage 26

findings_ref is optional but recommended for lineage traceability

continuity_context Rules

must contain all required keys

must use registered target core

must use allowed continuity scope

must identify a valid watcher receipt ref

must identify the Stage 24 output disposition ref

must identify runtime ref

must identify policy version used for intake decision

Stage 26 Allowed Actions

Stage 26 may:

validate the handoff

inspect findings only for policy admissibility

inspect lineage refs

emit intake / hold / failure receipt

update minimal intake state

Stage 26 may not:

rewrite watcher findings

mutate continuity canon/state

rerun watcher

publish any downstream child-core artifact

act as continuity mutation layer

Handoff Failure

If the Stage 25 → Stage 26 payload fails validation, Stage 26 must emit:

continuity_failure_receipt

It must not partially admit malformed input.

Handoff Summary

This contract exists so that watcher results can be evaluated for continuity significance without granting watcher hidden authority over memory.