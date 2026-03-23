# Child Core Inheritance Contract

## Purpose

This contract defines the minimum rules for how `PM_CORE` may propagate planning direction to child-core execution surfaces.

Inheritance exists to preserve lawful transfer of planning intent without collapsing PM authority into direct execution.

---

## Contract Role

The inheritance contract exists to:

- preserve the planning origin of propagated signal
- define the allowed inheritance handoff surface
- record which child core is being targeted
- preserve scope and planning context
- keep execution responsibility separate from planning responsibility

A child-core inheritance artifact is not direct execution by `PM_CORE`, canon authorship, or runtime ownership.

---

## Required Elements

Every child-core inheritance handoff must contain at minimum:

- `inheritance_id`
- `originating_authority`
- `target_child_core`
- `planning_summary`
- `strategic_signal`
- `scope`
- `tags`
- `created_at`
- `inheritance_status`

---

## Element Definitions

### `inheritance_id`
Unique governed identifier for the inheritance handoff.

### `originating_authority`
Must identify `PM_CORE` as the origin of planning direction.

### `target_child_core`
Declared child core intended to receive the planning signal.

### `planning_summary`
Bounded summary of the planning intent.

### `strategic_signal`
Declared strategic interpretation result used for handoff.

### `scope`
Declared scope of relevance such as domain, local, core, or system.

### `tags`
Controlled tags describing the inheritance handoff.

### `created_at`
UTC timestamp of handoff creation.

### `inheritance_status`
Declared handoff status such as prepared, issued, deferred, or rejected.

---

## Contract Rules

1. `PM_CORE` may only propagate to declared child-core surfaces.
2. Inheritance must preserve PM origin visibly.
3. Inheritance may not silently become execution.
4. The target child core must be explicit.
5. Handoff must remain traceable to the planning signal that produced it.
6. Inheritance language may not imply canon authority or runtime ownership.

---

## Invalid Inheritance Conditions

A child-core inheritance handoff is invalid if:

- required elements are missing
- target child core is unclear
- PM origin is omitted
- handoff attempts to contain direct execution steps as if PM performed them
- planning summary overstates authority beyond PM scope

---

## Boundary Rule

Valid inheritance handoffs may move from `PM_CORE` to declared child-core surfaces only through lawful interface pathways.

Receipt by a child core does not alter the originating authority of the planning signal.

---

## Summary

The child-core inheritance contract is the governed propagation artifact of `PM_CORE`.

It preserves authority separation by ensuring planning direction remains explicit, traceable, and bounded during downstream handoff.