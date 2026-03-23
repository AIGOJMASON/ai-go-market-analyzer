# Child Core to Watcher Interface

## Purpose

This interface preserves the lawful relationship between child-core execution surfaces and Watcher verification surfaces within AI_GO.

It exists so child-core artifacts, execution transitions, and local completion events may be verified without transferring monitoring authority to execution surfaces.

---

## Interface Rule

A child core may expose bounded artifacts or transitions to Watcher for verification.

Watcher verifies.
Child cores do not become the monitoring layer.

---

## What May Cross the Boundary

The following may lawfully move from child-core execution toward Watcher:

- output artifact references
- execution transition references
- completion events
- bounded handoff artifacts
- local status emissions

---

## What May Not Cross the Boundary

The following may not be delegated to child cores:

- artifact-verification ownership
- anomaly detection ownership
- sentinel health oversight
- cross-system monitoring orchestration
- root monitoring governance

---

## Summary

This interface preserves the distinction between domain execution and verification authority.