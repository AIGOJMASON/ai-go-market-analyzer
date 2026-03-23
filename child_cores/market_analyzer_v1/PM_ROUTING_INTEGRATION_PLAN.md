# MARKET_ANALYZER_V1 — PM ROUTING INTEGRATION PLAN

## Purpose

This document defines the routing-proof phase for `market_analyzer_v1` after validation, replay, and live shadow closure.

This is not autonomous activation.
This is not execution activation.

This phase exists to prove that PM can route into the child core lawfully while preserving authority, watcher validation, approval gating, and execution blocking.

---

## Routing Goal

The routing layer must prove that:

- PM_CORE can target `market_analyzer_v1` as an advisory-activated child core
- routed inputs preserve PM authority
- routed packets preserve the validated packet contract
- watcher validation remains intact on successful paths
- rejection behavior remains lawful on invalid market cases
- execution authority is not introduced through routing

---

## Scope

### In Scope
- PM-bound route request validation
- target-core resolution
- activation gating
- packet adaptation from routed shadow/live-style input
- runtime execution through the existing core
- watcher validation
- output surface preservation
- recommendation/advisory behavior only

### Out of Scope
- trade execution
- autonomous routing expansion
- registry activation mutation
- external feed integration
- non-PM entry points

---

## Planned Files

### `AI_GO/core/strategy/pm_market_analyzer_route.py`
PM routing surface for advisory-activated `market_analyzer_v1`.

### `AI_GO/tests/stage_market_analyzer_v1_pm_routing_probe.py`
Formal routing proof probe validating authority, target resolution, watcher behavior, and preserved execution blocking.

---

## Routing Rules

### 1. PM Authority Required
- `dispatched_by` must be `PM_CORE`
- no direct user or external dispatch accepted

### 2. Target Core Required
- `target_core` must resolve to `market_analyzer_v1`
- invalid targets must be rejected immediately

### 3. Activation Gating Required
- routing must require explicit activation approval
- approved mode is advisory only

### 4. Existing Runtime Must Remain Unchanged
- routed packets must enter the same validated runtime path
- no alternate runtime branch is allowed

### 5. Watcher Must Remain Mandatory
- successful routed outputs must preserve watcher validation
- watcher receipts remain part of the proof surface

### 6. Execution Must Remain Blocked
- `execution_allowed` must remain `false` on successful routed outputs
- routing may not create execution authority

---

## Planned Route Cases

### PM-ROUTE-001
Positive route case:
- PM-approved advisory activation
- necessity-qualified energy/fertilizer input
- valid rebound confirmation
- should route successfully
- watcher should pass
- execution remains blocked

### PM-ROUTE-002
Negative route case:
- PM-approved advisory activation
- non-necessity candidates only
- should reject at runtime
- no recommendations should be produced

### Rejection Cases
- invalid target core
- activation not approved
- non-PM dispatch source

These must all fail before runtime execution.

---

## Probe Success Criteria

The PM routing probe should prove that:

1. valid PM route resolves correctly
2. routed packet preserves PM authority fields
3. successful route preserves watcher validation
4. successful route preserves execution block
5. expected symbol(s) appear on positive path
6. non-necessity route rejects correctly
7. invalid target is rejected
8. activation-off route is rejected
9. non-PM dispatch is rejected
10. routing introduces no execution authority

---

## Exit Condition

PM routing integration is considered proven if:

- route probe passes fully
- no authority drift is observed
- no execution drift is observed
- watcher behavior remains intact
- runtime behavior matches prior replay/shadow proof

---

## Next Step After Routing Proof

If routing proof passes, the next lawful artifact is:

- routing closeout / ledger update
- optional registry/state review for real PM routing enablement

Still not allowed:
- autonomous execution
- approval bypass
- watcher bypass