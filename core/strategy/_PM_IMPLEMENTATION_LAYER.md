# PM Implementation Layer

## Purpose

This document defines the implementation layer for PM_CORE inside AI_GO.

PM_CORE is the strategic authority of the system.

It receives refinement bundles and determines strategic direction for
downstream execution domains.

PM_CORE does not perform research intake and does not execute domain work.

Its role is interpretation, prioritization, and inheritance control.

---

## Runtime Surface

PM implementation lives in:

core/strategy/

Primary modules:

- pm.py
- inheritance.py
- child_core_registry.py
- strategy_registry.py

---

## Receives

PM_CORE receives:

- refinement bundles
- interpreted research signals
- refinement interpretation surfaces

---

## Emits

PM_CORE emits:

- planning interpretations
- strategic priority signals
- child-core inheritance decisions

---

## Boundary Rules

PM_CORE must not:

- perform research screening
- modify continuity state
- bypass refinement
- directly execute domain cores

PM_CORE interprets signals and directs execution but does not perform
execution itself.

---

## Internal Components

### pm.py
Strategic interpretation surface.

### inheritance.py
Determines child-core inheritance structure.

### child_core_registry.py
Defines available execution cores.

### strategy_registry.py
Declares strategy-layer module surface.

---

## Connection Law

PM_CORE sits between refinement and domain execution.

Refinement bundles are interpreted strategically before being routed to
child cores.

---

## Summary

PM_CORE is the strategic planning authority that converts interpreted
research context into directed execution pathways for child cores.