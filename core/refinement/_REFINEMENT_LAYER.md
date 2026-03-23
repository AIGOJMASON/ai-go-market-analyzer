# Refinement Layer

## Purpose

The refinement layer transforms validated research packets into structured
refinement bundles suitable for strategic interpretation.

It performs multi-perspective interpretation across three refinement domains:

- strategic interpretation
- reasoning interpretation
- narrative interpretation

This preserves separation between raw research and planning authority.

---

## Runtime Surface

Refinement implementation lives in:

core/refinement/

Primary modules:

- refinement_gate.py
- pm_refinement.py
- reasoning_refinement.py
- narrative_refinement.py
- refinement_registry.py

Artifact output surface:

packets/refinement/

---

## Receives

Refinement receives:

- validated research packets
- research trust classification
- research screening results

---

## Emits

Refinement emits:

- refinement bundles
- refinement interpretation surfaces

---

## Boundary Rules

Refinement must not:

- perform PM planning decisions
- bypass research trust classification
- modify continuity state
- execute child cores

Refinement prepares structured interpretation only.

---

## Internal Components

### refinement_gate.py
Coordinates refinement execution.

### pm_refinement.py
Strategic interpretation surface.

### reasoning_refinement.py
Analytical interpretation surface.

### narrative_refinement.py
Narrative interpretation surface.

### refinement_registry.py
Declares refinement-layer module surface.

---

## Connection Law

Refinement sits between research and strategy.

Research packets are interpreted through multiple lenses before reaching
PM strategic authority.

---

## Summary

Refinement converts research truth into structured interpretive context
while preserving authority separation between research and planning.