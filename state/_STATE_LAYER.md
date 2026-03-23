# STATE Layer

## Purpose

The `state/` layer stores the **live mutable state** of the AI_GO system.

This layer represents the operational memory of the system across sessions and runtime activity.

Unlike `lib/`, which preserves canonical documents, the state layer stores evolving system data.

---

## Responsibilities

The state layer maintains:

- SMI continuity state
- runtime session status
- monitoring queues
- unresolved work items
- research and planning state references

---

## State Types

The state layer contains multiple categories:

### SMI

Continuity state for the system.

### Runtime

Active runtime session state and status.

### Watcher / Sentinel

Monitoring state and anomaly tracking.

### Research / Strategy

Working state relevant to intake and planning.

---

## Boundary Rule

State is mutable.

State may change during runtime.

State does not redefine canon.

---

## Summary

`state/` is the living memory of the system.