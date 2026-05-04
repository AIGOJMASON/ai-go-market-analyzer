# MIGRATION NOTES

## Purpose

Tracks structural and system-level transitions.

---

## Governance Requirement

All migration actions must respect:

- ingestion law
- mutation law
- execution gating

---

## Mutation Clarification

Any:

- receipt creation
- state change
- persistence

is classified as **mutation**

---

## Mutation Enforcement

All migration mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-core enforcement  

---

## Prohibited Behavior

- silent state changes
- undocumented mutation
- bypass of governance layers

---

## Summary

Migration is controlled transformation.

All changes are governed.