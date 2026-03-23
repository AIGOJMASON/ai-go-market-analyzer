# SHARED Layer

## Purpose

`core/shared/` is the reusable infrastructure layer of AI_GO.

It exists to provide common low-level utilities used by runtime, continuity, monitoring, research, PM, engines, and child-core support surfaces.

The shared layer does not own research authority, PM strategy, engine refinement, child-core execution, or canon preservation.

It is bounded support infrastructure.

---

## Authority Role

The shared layer is responsible for:

- filesystem path resolution
- governed identifier generation
- file and JSON input/output helpers
- timestamp generation
- lightweight schema validation
- general reusable helper functions

The shared layer is not responsible for:

- command routing
- research screening
- trust classification
- packet strategy
- runtime boot authority
- continuity ownership
- monitoring ownership
- canon authorship

---

## Internal Structure

The shared layer contains:

- `_SHARED_LAYER.md`
- `paths.py`
- `ids.py`
- `io_utils.py`
- `timestamps.py`
- `schemas.py`
- `utils.py`

These files provide foundational primitives for the rest of the system.

---

## Boundary Rules

1. Shared helpers must remain low-level and reusable.
2. Shared helpers may support authority layers, but may not replace them.
3. Shared helpers must not embed business logic from research, PM, or execution.
4. Shared helpers must preserve consistency across the system.

---

## Summary

`core/shared/` is the bounded infrastructure utility layer of AI_GO.

It exists to provide reusable primitives that keep the rest of the system consistent and clean.