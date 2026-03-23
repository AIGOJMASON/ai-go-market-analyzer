# Root Authorities

## Purpose

This document defines the root authorities of AI_GO.

Its purpose is to preserve the major governing surfaces of the system so authority boundaries remain explicit and stable across implementation change.

---

## Root Authorities of AI_GO

The root authorities are:

- CORE
- SMI
- WATCHER
- SENTINEL
- RESEARCH
- PM
- ENGINES
- LIB
- CHILD_CORE

These authorities form the major bounded organs of the system.

Each has a specific role and may not silently drift into another.

---

## Root Authority Principle

A root authority is a top-level system surface with:

- declared purpose
- bounded responsibility
- explicit relationship to other authorities
- preserved canonical definition
- implemented architecture beneath it

Root authorities are not interchangeable.

---

## Authority Separation Rule

Every root authority must remain distinct in meaning and function.

For example:

- Research validates signal
- PM interprets strategy
- Engines refine
- Child cores execute
- Lib preserves
- Core governs runtime
- SMI preserves continuity
- Watcher verifies artifacts
- Sentinel monitors system health

This separation is not stylistic.

It is structural law.

---

## Interaction Rule

Authorities may interact only through lawful handoff surfaces, contracts, interfaces, and declared downstream relationships.

No authority may seize another authority’s role through convenience.

---

## Canonical Dependency

Each root authority has a corresponding canonical definition document that preserves its meaning independent of implementation.

These definitions act as the preserved reference for architecture and runtime checking.

---

## Summary

`ROOT_AUTHORITIES.md` is the canonical map of top-level authorities in AI_GO.

It exists to preserve explicit authority separation across the entire operating system.