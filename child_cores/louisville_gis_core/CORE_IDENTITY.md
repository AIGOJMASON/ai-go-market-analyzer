# Child Core Inheritance Contract

## Purpose

This contract defines the minimum rules for how a child core may receive and preserve inheritance from `PM_CORE`.

Inheritance exists to ensure that downstream execution begins from explicit planning authority rather than undeclared intent.

---

## Contract Role

The inheritance contract exists to:

- preserve PM origin of inherited planning signal
- define the allowed handoff shape received by the child core
- record local inheritance state
- preserve scope and planning context
- keep execution responsibility separate from PM planning responsibility

A child-core inheritance record is not direct execution by `PM_CORE`, runtime ownership, or canon declaration.

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

## Contract Rules

1. A child core may only accept inheritance intended for that declared core.
2. PM origin must remain visible.
3. Inheritance may not be rewritten as if execution authored the planning signal.
4. Child-core execution begins only after lawful inheritance receipt.
5. Inheritance records must remain traceable to upstream PM artifacts.

---

## Invalid Conditions

Inheritance is invalid if:

- required elements are missing
- the target child core is unclear
- PM origin is omitted
- the handoff attempts to bypass declared planning provenance
- the artifact overstates child-core authority beyond execution scope

---

## Summary

This contract preserves lawful handoff from `PM_CORE` to a child core.

It ensures execution begins from explicit inherited planning direction rather than hidden authority drift.