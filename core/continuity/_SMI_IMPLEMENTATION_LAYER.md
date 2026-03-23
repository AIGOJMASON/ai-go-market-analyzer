# SMI Implementation Layer

## Purpose

`core/continuity/` is the implementation layer for SMI continuity inside AI_GO.

It exists to preserve live continuity state, accepted changes, unresolved items, and continuity-aware system memory across runtime activity.

This layer does not perform research intake, PM strategy, engine refinement, child-core execution, or canon archival.

It is the bounded continuity implementation surface.

---

## Authority Role

The continuity layer is responsible for:

- continuity state management
- accepted change recording
- unresolved continuity tracking
- continuity snapshot support
- lawful continuity reflection from runtime and other authorities

The continuity layer is not responsible for:

- runtime boot loading
- research screening
- trust classification
- strategic interpretation
- execution ownership
- archive ownership
- monitoring ownership

---

## Internal Structure

The continuity layer contains:

- `_SMI_IMPLEMENTATION_LAYER.md`
- `smi.py`
- `continuity_state.py`
- `change_ledger.py`
- `unresolved_queue.py`
- `continuity_registry.py`

Each file has a bounded role and must not silently absorb another.

---

## Continuity Flow

The lawful continuity path is:

Runtime Event  
↓  
SMI Continuity Surface  
↓  
Continuity State Update  
↓  
Change Ledger / Unresolved Queue  
↓  
Continuity Visibility

---

## Boundary Rules

1. Continuity must remain distinct from archive.
2. Continuity state must remain mutable and live.
3. Accepted changes and unresolved items must be explicit.
4. Continuity helpers may support the system, but may not replace runtime, PM, or research authority.
5. Continuity records preserve system coherence, not canonical law.

---

## Summary

`core/continuity/` is the bounded SMI implementation layer of AI_GO.

It exists to preserve live continuity, accepted changes, and unresolved state across runtime progression.