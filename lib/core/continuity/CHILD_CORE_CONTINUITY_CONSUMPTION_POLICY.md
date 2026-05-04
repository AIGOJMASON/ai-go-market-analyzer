# CHILD CORE CONTINUITY CONSUMPTION POLICY

## Purpose

Defines how child cores consume continuity data safely and lawfully.

---

## Source Requirement

All continuity data must originate from:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ PM  
→ continuity distribution  

Child cores may ONLY consume curated continuity outputs.

---

## Consumption Rules

Child cores:

- consume continuity as advisory context
- do not reinterpret source meaning
- do not generate new state independently

Continuity is:

- read-only unless mutation is explicitly approved
- bounded and traceable

---

## Mutation Clarification

Any persistence, memory update, or state change = **mutation**

All mutation must:

- be explicitly declared
- be classified (type, scope, intent)
- be traceable to governing decision

---

## Mutation Enforcement Chain

All mutation must pass:

State Authority  
→ Watcher validation  
→ Canon validation  
→ Request Governor  
→ Execution Gate  
→ Cross-core enforcement  

Without this chain, mutation is invalid.

---

## Prohibited Behavior

- implicit mutation through consumption
- child-core state creation without governance
- persistence outside approved mutation flow

---

## Summary

Continuity consumption is:

- controlled
- advisory-first
- mutation-gated