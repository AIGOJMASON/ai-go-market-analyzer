# PM to WATCHER Interface

## Purpose

This interface defines the lawful relationship between `PM_CORE` and watcher monitoring surfaces.

The interface exists so PM-relevant artifacts, transitions, and inheritance events may be verified without turning PM into a monitoring authority.

---

## Interface Rule

`PM_CORE` may expose bounded artifacts or transitions to watcher surfaces for verification.

Watcher verifies.
PM does not become the monitoring layer.

---

## What May Cross the Boundary

The following may lawfully move from PM toward watcher surfaces:

- inheritance packets
- propagation events
- PM transition references
- planning artifact references
- declared downstream handoff events

---

## What May Not Cross the Boundary

The following may not be delegated to PM through this interface:

- watcher verification ownership
- monitoring orchestration
- anomaly detection
- sentinel health oversight
- artifact-verification authority

`PM_CORE` emits planning artifacts.
Watcher verifies that events and artifacts occurred.

---

## Boundary Principle

Verification does not rewrite PM origin or strategic meaning.

PM remains planning authority.
Watcher remains verification authority.

---

## Summary

This interface preserves the distinction between strategic emission and monitoring verification.