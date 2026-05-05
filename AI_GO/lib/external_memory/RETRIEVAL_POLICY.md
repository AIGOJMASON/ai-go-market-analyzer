# EXTERNAL MEMORY RETRIEVAL POLICY

## Purpose

Defines how external memory is retrieved and used safely.

---

## Source Law

External memory must be tied to:

source or provider signal  
→ RESEARCH_CORE  
→ engine validation  
→ adapter  
→ PM  

Memory retrieval must not introduce new uncontrolled sources.

---

## Retrieval Rules

Retrieval is:

- read-only
- advisory
- traceable

---

## Mutation Clarification

Any:

- persist
- memory write
- promotion
- update

is considered **mutation**

---

## Mutation Enforcement

All mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-core enforcement  

---

## Prohibited Behavior

- direct memory writes during retrieval
- uncontrolled persistence
- memory acting as authority over governance

---

## Summary

Retrieval is read-only.

Mutation requires governance.