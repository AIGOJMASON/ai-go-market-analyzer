# MARKET_ANALYZER_V1 — LIVE SHADOW TEST PLAN

## Purpose

This document defines the first live shadow validation layer for `market_analyzer_v1`.

This is not activation.
This is not execution.
This is not autonomy.

It is a governed shadow harness that adapts manually refreshed or live-style market inputs into the existing PM-bound packet flow and validates that the child core behaves lawfully under shadow conditions.

---

## Objectives

The live shadow layer must prove that:

- the existing core can be exercised using shadow-mode inputs
- those inputs can be normalized into the same PM-style packet shape already accepted by runtime
- watcher verification remains intact on successful paths
- recommendation outputs remain approval-gated
- `execution_allowed` remains `false`
- negative shadow cases reject lawfully without mutating architecture

---

## Files

### `ui/live_shadow_packet_adapter.py`
Adapts operator/manual/live-style shadow inputs into lawful PM-style packets using the validated live packet pattern.

### `ui/live_shadow_runner.py`
Runs shadow inputs through:
1. adapter
2. existing `run(packet)` runtime
3. watcher verification
4. dashboard/output view generation

### `ui/live_shadow_cli_report.py`
Renders human-readable CLI output for shadow runs.

### `tests/stage_market_analyzer_v1_live_shadow_probe.py`
Formal probe validating the live shadow harness.

---

## Shadow Rules

### Authority
- parent authority remains `PM_CORE`
- target core remains `market_analyzer_v1`
- no independent child-core authority is introduced

### Activation State
- all shadow packets must be tagged as:
  - `shadow_mode: true`
  - `activation_state: shadow_only`
  - `execution_block_required: true`

### Runtime Rule
- existing runtime path must remain unchanged
- no shadow-specific execution engine may be introduced

### Output Rule
- output remains structured
- watcher receipts remain preserved on successful execution paths
- human approval gate remains required

---

## Initial Shadow Cases

### LIVE-SHADOW-001
Positive shadow case:
- confirmed shock
- necessity-qualified sectors
- valid rebound confirmation
- should produce recommendation(s)
- watcher should pass
- execution must remain blocked

### LIVE-SHADOW-002
Negative shadow case:
- confirmed shock
- non-necessity sectors only
- should reject with runtime error
- no recommendation should be produced

---

## Success Criteria

The live shadow phase is considered valid if:

1. the adapter produces lawful packets
2. the runner records all shadow cases without harness failure
3. the positive case yields at least one recommendation
4. the positive case preserves:
   - watcher success
   - `execution_allowed = false`
5. the negative case rejects with the expected runtime reason
6. probe passes fully

---

## Exit Condition

If live shadow passes, the next lawful step is deeper shadow expansion:
- more live-style input sets
- more source variants
- broader regime coverage

But still:
- no activation
- no autonomous execution
- no bypass of human approval