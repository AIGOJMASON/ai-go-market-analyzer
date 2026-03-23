# PM to SMI Interface

## Purpose

This interface defines the lawful relationship between `PM_CORE` and SMI continuity surfaces.

The interface exists so PM planning outcomes, significant state changes, or unresolved planning items may be reflected in continuity without turning PM into continuity ownership.

---

## Interface Rule

`PM_CORE` may send bounded continuity-relevant artifacts or state signals to SMI.

SMI preserves continuity state.
PM does not become the continuity layer.

---

## What May Cross the Boundary

The following may lawfully move from PM toward SMI surfaces:

- planning milestones
- accepted PM state changes
- unresolved planning items
- inheritance-relevant continuity notes
- bounded handoff references

---

## What May Not Cross the Boundary

The following may not be delegated to PM through this interface:

- continuity ownership
- continuity-state orchestration
- unresolved queue ownership
- change-ledger authority
- long-term continuity governance

`PM_CORE` signals.
SMI preserves continuity.

---

## Boundary Principle

Continuity reflection does not alter the originating authority of the PM artifact that produced it.

PM remains planning authority.
SMI remains continuity authority.

---

## Summary

This interface preserves the distinction between live strategic planning and long-range continuity management.